const config = window.VanillaZotero.config;
const readCookie = window.VanillaZotero.Util.readCookie;
const getUserID =  window.VanillaZotero.Util.getUserID;

const sessionCookie = readCookie(config.zoteroSessionCookieName);

//for image links that have been uploaded to the forums, find the matching urls and swap in details disclosure element
//to optionally show the image
function decorateForumImages() {
	if (!config.forumImageDomain) {
		console.error('No forumImageDomain set');
		return;
	}
	//get the link elements for forums images that vanilla created server-side and replace with
	//disclosure element
	let postLinks = document.querySelectorAll('div.Message a:not(forum-image-disclosure a)');
	postLinks.forEach(function(link) {
		let href = link.href;
		if(href.startsWith(`https://${config.forumImageDomain}/images/forums`)) {
			let el = document.createElement('forum-image-disclosure');
			el.setAttribute('open', '');
			el.setAttribute('href', href);
			link.replaceWith(el);
		}
	});
}

//custom element to replace forum images with a disclosure widget
class ForumImageDisclosure extends HTMLElement {
	static get observedAttributes() {
		return ["href", "open"];
	}
	
	connectedCallback() {
		let template = document.getElementById('forum-disclosure-template');
		let templateContent = template.content;

		this.appendChild(templateContent.cloneNode(true));
		if (this.hasAttribute('href')) {
			this.querySelector('img.forum-upload-image').setAttribute('src', this.getAttribute('href'));
		}
		/*
		if (this.hasAttribute('open')) {
			this.querySelector('summary').innerHTML = `Hide Image`;
			this.querySelector('details').setAttribute('open', '');
		} else {
			this.querySelector('summary').innerHTML = `Show Image`;
			this.querySelector('details').removeAttribute('open');
		}

		this.querySelector('summary').addEventListener('click', (evt) => {
			evt.preventDefault();
			this.toggleAttribute('open');
		});
		*/
	}

	attributeChangedCallback(name, oldValue, newValue) {
		if (!this.isConnected) {
			return;
		}
		if (name == 'href') {
			this.querySelector('img.forum-upload-image').setAttribute('src', newValue);
		}/* else if(name == 'open') {
			if (newValue == null) {
				this.querySelector('summary').innerHTML = `Show Image`;
				this.querySelector('details').removeAttribute('open');
			} else {
				this.querySelector('summary').innerHTML = `Hide Image`;
				this.querySelector('details').setAttribute('open', '');
			}
		}*/
	}
}

//custom element to upload/delete images for forum posts by selecting with a file dialog
//or dragging and dropping. When image is uploaded, a link is automatically inserted into
//the textarea being edited. That url will be detected and rendered as an image whe the
//post is viewed. When editing a post, uploaded image urls are detected and listed so the
//user can delete them. When deleted, the url is removed from the text of the post.
class ForumImages extends HTMLElement {
	files = [];
	uploadMessages = [];
	uploadedUrls = [];
	
	connectedCallback() {
		const template = document.getElementById('forum-images-template');
		const templateContent = template.content;
		
		this.appendChild(templateContent.cloneNode(true));

		const dropZoneEl = this.textbox;// this.querySelector('div.image-drop-zone');
		// console.log('set dropzone to textbox');
		// console.log(dropZoneEl);

		const handleFiles = (selectedFiles) => {
			[...selectedFiles].forEach((file, i) => {
				let fileSizeKB = file.size / 1024;
				let fileSizeMB = fileSizeKB / 1024;
				// console.log(file);
				console.log(`… file[${i}].name = ${file.name}, ${fileSizeKB}KB (${fileSizeMB}MB)`);
				const extensionRegex = /(\.png|\.gif|\.jpg|\.jpeg)$/i;
				if (!extensionRegex.test(file.name)) {
					alert(`Sorry, that file is not allowed. Images must be .png, .gif, .jpg, or .jpeg`);
					return;
				}
				if (fileSizeMB > config.fileSizeLimitMB) {
					alert(`File too large. Must be under ${config.fileSizeLimitMB} MB.`);
					return;
				}
				this.files.push(file);
				this.uploadFile(file).then(() => {
					this.previewUploadedUrls();
					gdn.informMessage("Image uploaded");
					//save draft with image link
					let draftButton = document.querySelector('a.Button.DraftButton');
					if (!draftButton) {
						draftButton = document.querySelector('input.Button.DraftButton');
					}
					draftButton.click();
				});
			});
		};
	
		const imageUploadDropHandler = (ev) => {
			// console.log("imageUploadDropHandler");
			let files = false;
			if (ev.type == 'paste') {
				if (!ev.clipboardData.files.length) {
					return;
				}
				// Prevent default behavior (Prevent file from being opened)
				ev.stopPropagation();
				ev.preventDefault();
				
				files = ev.clipboardData.files;
			} else if (ev.type == 'drop') {
				// Prevent default behavior (Prevent file from being opened)
				ev.stopPropagation();
				ev.preventDefault();

				files = ev.dataTransfer.files;
				dropZoneEl.classList.remove('highlight');
			}
			
			handleFiles(files);
		};
		
		const dragOverHandler = (ev) => {
			// console.log("File(s) in drop zone");
			// Prevent default behavior (Prevent file from being opened)
			ev.stopPropagation();
			ev.preventDefault();
	
			dropZoneEl.classList.add('highlight');
		};
		const dragEnterHandler = dragOverHandler;
	
		const dragleaveHandler = (evt) => {
			dropZoneEl.classList.remove('highlight');
	
		};
	
		//set drag/drop handlers
		dropZoneEl.addEventListener('drop', imageUploadDropHandler);
		dropZoneEl.addEventListener('paste', imageUploadDropHandler);
		dropZoneEl.addEventListener('dragover', dragOverHandler);
		dropZoneEl.addEventListener('dragenter', dragEnterHandler);
		dropZoneEl.addEventListener('dragleave', dragleaveHandler);

		document.querySelector('.add-image-button').addEventListener('click', (evt) => {
			evt.preventDefault();
			evt.stopPropagation();
			this.querySelector('.fileElem').showPicker();
		});

		this.querySelector('.fileElem').addEventListener('change', function(evt) {
			handleFiles(this.files);
		});

		//perform cleanup of images triggered by Vanilla actions.
		$(document).on('click', '.CommentButton, .PreviewButton, .DraftButton', () => {
			this.deleteRemovedFiles(this.uploadedUrls, this.textbox.value);
		});
	}

	async uploadFile(file) {
		// console.log('uploadFile');
		let formData = new FormData()

		formData.append('forum_image', file);

		let headers = {
			Authorization: sessionCookie,
		};

		// console.log(`fetching ${config.uploadUrl}`);
		try {
			let resp = await fetch(config.uploadUrl, {
				credentials: 'include',
				method: 'POST',
				headers: headers,
				// mode: "no-cors"
				body: formData
			});
			//get json result from response
			let data = await resp.json();
			if(!resp.ok) {
				// console.log(data);
				if(data.error) {
					throw new Error(data.error);
				}
				throw data;
			}
			//success, get url from response
			if (!data.url) {
				throw new Error('no url result from image upload');
			}
			this.uploadedUrls.push(data.url);
			// addImageUrlToForm(data.url);
			this.addImageLinkToPost(data.url);
		} catch(err) {
			// Error. Inform the user
			console.error(err);
			alert("There was an error processing your image");
		};
	};

	async deleteUploadedFile(url) {
		// console.log('deleteUploadedFile');

		const filePath = url.substring(url.indexOf('images/forums/u'));
		const queryString = encodeURIComponent(filePath);
		const requestUrl = `${config.uploadUrl}?forum_image=${queryString}`;

		let headers = {
			Authorization: sessionCookie,
		};

		// console.log(`fetching ${requestUrl}`);
		return fetch(requestUrl, {
			credentials: 'include',
			method: 'DELETE',
			headers: headers,
			// mode: "no-cors"
		}).then((resp) => {
			//get json result from response
			if(resp.ok) {
				return resp.json();
			} else {
				throw resp.json();
			}
		}).then((data) => {
			this.removeImageLinkFromPost(url);
			//remove from list of uploaded urls and refresh previews to remove
			const index = this.uploadedUrls.indexOf(url);
			// console.log(this.uploadedUrls);
			this.uploadedUrls.splice(index, 1);
			// console.log(this.uploadedUrls);
		}).catch((err) => {
			// Error. Inform the user
			console.error(err);
		});
	};

	//delete any of the files that have been uploaded but have had the links removed
	//from the post text
	deleteRemovedFiles(uploadedUrls, textValue) {
		// console.log('deleteRemovedFiles');
		// console.log(uploadedUrls);
		// console.log(textValue);
		uploadedUrls.forEach((url) => {
			// console.log(url);
			if (!textValue.includes(url)) {
				console.log(`${url} not found`);
				this.deleteUploadedFile(url);
				gdn.informMessage(`Deleting removed file ${url}`);
			}
		});
	}

	//just add url and let forum auto-link
	addImageLinkToPost(url) {
		// console.log('addImageLinkToPost');
		const textbox = this.textbox;
		// console.log(textbox);
		// const linkText = `<a href="${url}">Saved Image</a>`;
		// textbox.value = textbox.value + `\n\n${linkText}\n`;
		let insertString = `${url}`;
		
		if (textbox.selectionStart || textbox.selectionStart == '0') {
			let startPos = textbox.selectionStart;
			let endPos = textbox.selectionEnd;
			let preText = textbox.value.substring(0, startPos);
			let postText = textbox.value.substring(endPos);
			insertString = (preText.endsWith("\n") ? '' : "\n") + insertString + (postText.startsWith("\n") ? '' : "\n");
			textbox.value = preText	+ insertString + postText;
			
			textbox.focus();
			textbox.setSelectionRange(startPos + insertString.length, startPos + insertString.length);
		} else {
			let preText = textbox.value;
			insertString = (preText.endsWith("\n") ? '' : "\n") + insertString;
			textbox.value = preText + insertString;

			textbox.focus();
			textbox.setSelectionRange(textbox.value.length);
		}

		gdn.autosize(textbox);
	};

	//remove forum image links from comment textarea
	removeImageLinkFromPost(url) {
		const textbox = this.textbox;
		textbox.value = textbox.value.replaceAll(url, '');
		textbox.focus();
		textbox.selectionEnd = textbox.value.length;
	};


	//detect urls matching uploaded forum images in the comment textarea
	detectUserImageUrls() {
		// console.log('detectUserImageUrls');
		const textbox = this.textbox;
		// console.log(textbox);
		if (!textbox) {
			return;
		}
		const forumImageRegex = /http[\S]*\/images\/forums\/u[0-9]+\/[a-zA-Z0-9]{20}(\.jpg|\.png|\.gif)?/g;
		const matches = textbox.value.match(forumImageRegex);
		if (matches == null) {
			console.log('no matches in textbox value');
			return;
		}

		const loggedInUserID = getUserID();
		if(!loggedInUserID) {
			console.log('no logged in user');
			return;
		}

		//if matches are for current user, add them to uploaded URLs array to allow deletion
		matches.forEach((url) => {
			let userIDMatches = url.match(/forums\/u([0-9]+)\//);
			let userID = userIDMatches[1];
			if (userID == loggedInUserID) {
				console.log('adding url to this.uploadedUrls');
				console.log(url);
				this.uploadedUrls.push(url);
			}
		});
		if (this.uploadedUrls.length) {
			this.previewUploadedUrls();
		}
	};

	previewUploadedUrls() {
		return;
	}

	reset() {
		this.files = [];
		this.uploadMessages = [];
		this.uploadedUrls = [];
	}
}

window.customElements.define('forum-images', ForumImages);
window.customElements.define('forum-image-disclosure', ForumImageDisclosure);

function initForumImages() {
	//create forum-image element in container
	const FIContainer = document.querySelector('#forum-images-container');
	if (FIContainer) {
		const forumImages = document.createElement('forum-images');
		//add textbox before adding to document so it's available in connectedCallback
		forumImages.textbox = document.querySelector('form#Form_Comment textarea[name="Body"]') ?? document.querySelector('div#DiscussionForm textarea#Form_Body');
		FIContainer.appendChild(forumImages);
		forumImages.detectUserImageUrls();

	}
}

jQuery(document).ready(function($) {
	//decorate image urls in rendered posts
	decorateForumImages();
	initForumImages();

	//re-run decorate when comment is previewed or submitted async and added
	$(document).on('CommentAdded PreviewLoaded', function(){
		setTimeout(decorateForumImages, 10);
	});

	//re-run init when comment is added and new comment form
	// $(document).on('CommentAdded', function(){
		// setTimeout(initForumImages, 10);
	// });
	
	//add image upload component to comments being edited
	//add event listener for EditCommentFormLoaded using jQuery because it's a jQuery event
	//and native event handler doesn't catch it
	jQuery(document).on('EditCommentFormLoaded', function(evt, container) {
		const editCommentForumImages = document.createElement('forum-images');
		const editCommentForm = container.get(0).querySelector('.EditCommentForm');
		const textbox = editCommentForm.querySelector('textarea');
		editCommentForumImages.textbox = textbox;
		editCommentForm.appendChild(editCommentForumImages);
		editCommentForumImages.detectUserImageUrls();
	});

	//remove forum-images elements when a comment is submitted async so there is no reload to remove them
	jQuery(document).on('CommentAdded CommentEditingComplete', function(evt) {
		document.querySelectorAll('forum-images').forEach(function(el){
			el.reset();
		});
	})

});
