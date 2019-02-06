function initPanes() {
    // https://split.js.org/
    Split(['#left-pane', '#right-pane'], {
        sizes: [25, 75],
        gutterSize: 5,
        cursor: 'row-resize',
    });

}

document.addEventListener("DOMContentLoaded", initPanes);