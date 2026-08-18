
//component for dialog content (don't do the full dialog because safari won't extend native elements)
class DialogContent extends HTMLElement {
	dialogEl;

	connectedCallback() {
		// console.log('DialogContent::connectedCallback');
		let template = document.getElementById('dialog-content');
		let templateContent = template.content;

		this.appendChild(templateContent.cloneNode(true));
		this.querySelector('.close-dialog-button').addEventListener('click', (evt) => {
			this.dialogEl.close(null);
		});
		this.querySelector('button.dialog-ok').addEventListener('click', (evt) => {
			evt.preventDefault();
			this.dialogEl.close(null);
		});
	};

	setBody(newBody) {
		// console.log('DialogContent::setBody');
		this.querySelector('div.dialog-body').innerHTML = newBody;
	};

	showModal() {
		this.dialogEl.showModal();
	};
	
	close(retVal) {
		this.dialogEl.close(retVal);
	};
}

window.customElements.define('dialog-content', DialogContent);

jQuery(document).ready(function($) {
	//array of regular expressions to test against and the suggested reading if matched
	const discussionTitleSuggestions = [
		{
			regex: /word/i,
			suggestionUrl: 'https://www.zotero.org/support/word_processor_integration',
			suggestionText: 'Word Processor Integration'
		},
		{
			regex: /style/i,
			suggestionUrl: 'https://github.com/citation-style-language/styles/wiki/Requesting-Styles',
			suggestionText: 'Requesting Styles'
		},
		{
			regex: /CNKI/i,
			suggestionUrl: 'https://forums.zotero.org/discussion/109525/an-error-occurred-while-saving-using-cnki',
			suggestionText: 'An error occurred while saving using CNKI'
		},
	];

	const discussionBodySuggestions = [
		{
			regex: /^\s*\[Describe the issue you're reporting\.\]\s*$/i,
			suggestionHtml: "Please describe the actual problem that you're experiencing. See <a href='https://www.zotero.org/support/reporting_problems#provide_steps_to_reproduce'>Steps to Reproduce</a> for the kind of description we need.",
			blockSubmit: true,
		}
	];

	const commentSuggestions = [
		{
			regex: /similar (problem|issue)/i,
			suggestionHtml: 'If you think you have a similar problem but are not seeing the identical behavior described in this thread, you should <a href="/post/discussion">start a new discussion</a> instead. See <a href="https://www.zotero.org/support/reporting_problems">Reporting Problems</a> for the details needed to allow Zotero developers and others to help you most effectively.',
		}
	];

	//initialize dialog for body suggestions
	const commentSuggestionsDialogEl = document.querySelector('dialog#CommentSuggestions');
	const commentSuggestionDialogContent = document.createElement('dialog-content');
	commentSuggestionDialogContent.dialogEl = commentSuggestionsDialogEl;
	commentSuggestionsDialogEl.appendChild(commentSuggestionDialogContent);
	let commentDialogShown = false;

	//elements to run checks on
	const discussionInputBox = document.querySelector('input[name="Name"]');
	const discussionBodyBox = document.querySelector('#DiscussionForm textarea#Form_Body[name="Body"]');
	const commentInputBox = document.querySelector('#Form_Comment textarea');
	
	//get the suggestions that match based on a given string
	const getMatchedSuggestions = function(value, suggestions) {
		// console.log("getSuggestions");
		let matchedSuggestions = [];
		for(const suggestion of suggestions) {
			if (suggestion.regex.test(value)) {
				matchedSuggestions.push(suggestion);
			}
		}
		return matchedSuggestions;
	}

	//check body for suggestion matches and show a dialog with suggestion content
	//if showOnce is set, don't show the dialog again for 5 minutes
	const checkBodySuggestions = function(body, suggestions, showOnce=false) {
		// console.log("checkBodySuggestions");
		if (commentDialogShown) {
			return;
		}
		let matchedSuggestions = getMatchedSuggestions(body, suggestions);
		if (matchedSuggestions.length > 0) {
			commentSuggestionDialogContent.setBody(matchedSuggestions[0].suggestionHtml);
			commentSuggestionDialogContent.showModal();
			if (showOnce) {
				commentDialogShown = true;
				setTimeout(()=> {
					//allow dialog to be shown again after 5 minutes
					commentDialogShown = false;
				}, 300000);
			}
			return true;
		}
		return false;
	}

	//When a discussion title is entered, check it for some key words that we may want to
	//suggest a documentation page for in order to short-circuit some common questions
	//These are presented as "You may want to read:" just above the dicsussion title that
	//was just entered.
	if (discussionInputBox) {
		discussionInputBox.addEventListener('blur', function(e) {
			const title = $('input[name="Name"]').val();
			let matchedSuggestions = getMatchedSuggestions(title, discussionTitleSuggestions);

			if(matchedSuggestions.length > 0){
				$('#SuggestedReading').show();
				$('#suggestedReadingList').empty();
				for(let suggestion of matchedSuggestions){
					let linkHtml = `<a href='${suggestion.suggestionUrl}'>${suggestion.suggestionText}</a>`;
					$('#suggestedReadingList').append('<li>' + linkHtml + '</li>');
				}
			} else {
				$('#SuggestedReading').hide();
			}
		});
	}

	//if this is a start discussion page
	if (discussionBodyBox) {
		//add handler to discussion form that jQuery will call before ajax submission
		//note that this will also trigger after 1 minute because Vanilla automatically presses the save draft button
		document.querySelector('#DiscussionForm form').onBeforeDiscussionSubmit = function(evt, frm, btn) {
			if (btn.id != "Form_PostDiscussion") {
				return;
			}
			//if we have a suggestion, add a sentinel to the form to prevent submission after showing suggestion
			let haveSuggestion = checkBodySuggestions(discussionBodyBox.value, discussionBodySuggestions, false);
			if (haveSuggestion) {
				//prevent Vanilla's ajax form submission
				// console.log("adding hidden input to form to skip submission")
				$("<input />").attr("type", "hidden")
					.attr("name", "zotero_posthelp_prevent_submit")
					.attr("value", "1")
					.appendTo("#DiscussionForm form");
			} else {
				//make sure we don't still have the sentinel from a previous submission
				let s = document.querySelector('input[name="zotero_posthelp_prevent_submit"]');
				if (s) {
					s.remove();
				}
			}
		};
		
		//when the form actually gets submitted normally (not via Vanilla's ajax submit) prevent it
		//if javascript is enabled, it will be submitted via ajax, if disabled this won't interfere
		document.querySelector('#DiscussionForm form').addEventListener('submit', function(evt) {
			evt.preventDefault();
		});
	}

	//when the comment box blurs, test its content against regexes (currently only similar issue/problem)
	//if matched, show dialog which will prevent submission when shown
	//after dialog is dismissed, don't show again for 5 minutes so user can choose to submit the comment
	//if they choose
	if (commentInputBox) {
		if (commentInputBox) {
			commentInputBox.addEventListener('blur', function(evt) {
				checkBodySuggestions(commentInputBox.value, commentSuggestions, true);
			});
		}
	}
});
