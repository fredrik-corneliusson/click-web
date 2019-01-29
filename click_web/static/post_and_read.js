function post_and_read() {
    // alert(input_form.reportValidity());
    var input_form = document.getElementById("inputform");
    var output_div = document.getElementById("output")
    // TODO: Why is this never false?!
    if (!input_form.reportValidity()) {
        // not valid form values, abort.
        return false;
    }

    fetch(command_url, {
        method: "POST",
        body: new FormData(input_form),
    })
        .then(function (response) {
            if (response.body === undefined) {
                // body not supported (FireFox?)
                // It is supported by Firefox but fetch streams are not enabled by default
                // to enable in FF go to about:config and toggle "javascript.options.streams" settings to true
                response.text()
                    .then(text => output_div.innerHTML = text);
                return;

            }
            var reader = response.body.getReader();
            var decoder = new TextDecoder();
            var text = "";

            function read() {
                return reader.read().then(function (result) {
                    text += decoder.decode(result.value);

                    if (!result.done) {
                        output_div.innerHTML = text;
                        return read();
                    }

                })
            }

            return read();
        });

    return false;
}


