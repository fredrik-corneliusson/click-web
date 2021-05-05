function copyOutputToClipboard() {
    var range = document.createRange();
    range.selectNode(document.getElementById("output"));
    window.getSelection().removeAllRanges(); // clear current selection
    window.getSelection().addRange(range); // to select text
    document.execCommand("copy");
    window.getSelection().removeAllRanges();// to deselect
}
