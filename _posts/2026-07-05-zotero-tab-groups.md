---
layout: post
title: Zotero Tab Groups - Edge-style Tab Organization for Zotero
date: 2026-07-05 10:00:00-0400
description: A Zotero plugin that adds grouped tab options, similar to Microsoft Edge's tab groups.
tags: zotero productivity plugins
categories: tools
featured: true
---

I built a Zotero plugin that brings Microsoft Edge-style tab groups to Zotero's horizontal tab bar. If you work with multiple PDFs across different projects, this plugin helps you organize, collapse, and manage your tabs efficiently.

## What It Does

Zotero Tab Groups lets you organize open PDF tabs into named, colored, collapsible clusters. Group tabs by project, collapse the ones you're not using, and find everything again after a restart.

## Key Features

- **Group tabs** - Right-click any PDF tab → Add to Group → New Group…
- **8 colors + custom names** - Each group gets a colored pill in the tab strip and a colored underline across its member tabs
- **Auto-contiguous** - Grouped tabs always stay next to each other
- **Drag and drop** - Drop a tab onto a group's pill to add it; drag a tab into the middle of a group to join it, or drag it out to leave
- **Collapse/expand** - Click a group's pill to hide its tabs behind the pill (shows the tab count); click again to expand
- **Manage groups** - Double-click a pill to rename; right-click it for color, collapse, close-all, and ungroup options
- **Survives restarts** - Membership is keyed to the underlying Zotero item, so reopening a PDF puts its tab back in its group

## Installation

1. Download the latest `.xpi` from the [releases page](https://github.com/shourovj/zotero-tab-groups/releases/latest) (in Firefox, right-click → Save Link As… so it doesn't try to install there)
2. In Zotero: **Tools → Plugins → ⚙️ → Install Plugin From File…** and select the `.xpi`
3. Open some PDFs and right-click a tab to start grouping

Compatible with Zotero 7, 8, and 9 (developed and tested on Zotero 9).

## Usage

| Action | How |
|--------|-----|
| Create a group | Right-click a tab → **Add to Group → New Group…** |
| Add a tab to a group | Right-click → **Add to Group → *group name***, or drag the tab onto the group's pill |
| Remove a tab | Right-click → **Remove from "*group*"**, or drag the tab out of the group |
| Collapse/expand | Click the group's pill |
| Rename | Double-click the pill, or right-click it → **Rename Group…** |
| Change color | Right-click the pill → **Color** |
| Close all tabs in a group | Right-click the pill → **Close Tabs in Group** |
| Dissolve a group | Right-click the pill → **Ungroup** |

**Tip:** Selecting a hidden tab of a collapsed group (e.g. with keyboard shortcuts) auto-expands the group.

## How It Works

Zotero 7+ renders its tab bar as a React component, so this plugin never injects children into the strip. Instead it:

- Decorates the React-owned tab nodes with classes/styles, re-applied by a `MutationObserver` after every React render
- Draws group pills and underline frames in an overlay layer outside the React root, positioned from the member tabs' bounding rectangles
- Reorders tabs only through the official `Zotero_Tabs.move()` API
- Persists groups and membership (keyed by item ID) as JSON in a Zotero pref

## Development

```bash
git clone https://github.com/shourovj/zotero-tab-groups.git
cd zotero-tab-groups
npm install
cp .env.example .env   # set your Zotero binary (and optionally profile) path

npm start              # launch Zotero with the plugin + hot reload
npm run build          # production build → .scaffold/build/zotero-tab-groups.xpi
npm test               # run the in-app mocha test suite inside a live Zotero
```

The test suite exercises the real tab bar DOM in a sandboxed Zotero profile: grouping, contiguity, collapse, drag-assignment, persistence, and context-menu injection.

## Source Code

The plugin is open source under the AGPL-3.0 license. Find it on GitHub: [shourovj/zotero-tab-groups](https://github.com/shourovj/zotero-tab-groups)
