function post_and_read() {
    var input_form = document.getElementById("inputform");
    // TODO: Why is this never false?!
    if (!input_form.reportValidity()) {
        // not valid form values, abort.
        return false;
    }
    var output_header_div = document.getElementById("output-header")
    var output_div = document.getElementById("output")
    var output_footer_div = document.getElementById("output-footer")
    // clear old content
    output_header_div.innerHTML = '';
    output_div.innerHTML = '';
    output_footer_div.innerHTML = '';
    // show script output
    output_header_div.hidden = false;
    output_div.hidden = false;
    output_footer_div.hidden = false;

    function getInsertFunc(part, current_elem, current_func) {
        // method analyzes the part, and changes output func
        // if needed.
        if (part.includes(' START ')) {
            if (part.includes(' HEADER ')) {
                return [output_header_div, output_header_div.insertAdjacentHTML];
            } else if (part.includes(' FOOTER ')) {
                return [output_footer_div, output_footer_div.insertAdjacentHTML];
            } else {
                throw "Unknown part:" + part;
            }
        } else if (part.includes(' END ')){
            // plain text again
            return [output_div, output_div.insertAdjacentText];
        } else {
            // no change
            return [current_elem, current_func];
        }
    }

    fetch(command_url, {
        method: "POST",
        body: new FormData(input_form),
        // for fetch streaming only accept plain text, we wont handle html
        headers: {Accept: 'text/plain'}
    })
        .then(response => {
            if (response.body === undefined) {
                // body not supported in FireFox by default!
                // It is supported in FF by setting "javascript.options.streams" to true in "about:config"
                response.text()
                    .then(text => output_div.innerHTML = text);
                return;

            }
            var reader = response.body.getReader();
            var decoder = new TextDecoder();

            function split_click_web_sections(chunk) {
                chunk.search(/<!-- CLICK_WEB/)
            }

            async function aread() {
                while (true) {
                    const result = await reader.read();
                    let chunk = decoder.decode(result.value);
                    // https://stackoverflow.com/questions/11515383/why-is-element-innerhtml-bad-code
                    console.log(chunk);
                    let insert_func = output_div.insertAdjacentText;
                    let elem = output_div;

                    if (chunk.includes('<!-- CLICK_WEB')) {
                        // there are one or more click web special sections, use regexp split chunk into parts
                        // and process them individually
                        let parts = chunk.split(/(<!-- CLICK_WEB [A-Z]+ [A-Z]+ -->)/);
                        for (let i = 0; i < parts.length -1 ; i++) {
                            let part = parts[i];
                            [elem, insert_func] = getInsertFunc(part, elem, insert_func);
                            if (part.startsWith('<!-- ')) {
                                continue;
                            } else {
                                insert_func.call(elem,'beforeend', part);

                            }

                        }

                    } else {
                        insert_func.call(elem,'beforeend', chunk);
                    }

                    if (result.done) {
                        break
                    }
                }
            }

            return aread();
        });

    return false;
}


