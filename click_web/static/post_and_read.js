let REQUEST_RUNNING = false;

function postAndRead(commandUrl) {
    if (REQUEST_RUNNING) {
        return false;
    }

    input_form = document.getElementById("inputform");
    let submit_btn = document.getElementById("submit_btn");

    try {
        REQUEST_RUNNING = true;
        submit_btn.disabled = true;
        let runner = new ExecuteAndProcessOutput(input_form, commandUrl);
        runner.run();
    } catch (e) {
        console.error(e);

    } finally {
        // if we executed anything never post form
        // as we do not know if form already was submitted.
        return false;

    }
}

class ExecuteAndProcessOutput {
    constructor(form, commandPath) {
        this.form = form;
        this.commandUrl = commandPath;
        this.decoder = new TextDecoder('utf-8');
        this.output_header_div = document.getElementById("output-header")
        this.output_wrapper_div = document.getElementById("output-wrapper")
        this.output_div = document.getElementById("output")
        this.output_footer_div = document.getElementById("output-footer")
        // clear old content
        this.output_header_div.innerHTML = '';
        this.output_div.innerHTML = '';
        this.output_footer_div.innerHTML = '';
        // show script output
        this.output_header_div.hidden = false;
        this.output_wrapper_div.hidden = false;
        this.output_footer_div.hidden = false;
    }

    run() {
        let submit_btn = document.getElementById("submit_btn");
        this.post(this.commandUrl)
            .then(response => {
                this.form.disabled = true;
                let reader = response.body.getReader();
                return this.processStreamReader(reader);
            })
            .then(_ => {
                REQUEST_RUNNING = false
                submit_btn.disabled = false;
            })
            .catch(error => {
                    console.error(error);
                    REQUEST_RUNNING = false;
                    submit_btn.disabled = false;

                }
            );
    }

    post() {
        console.log("Posting to " + this.commandUrl);

        // Create an object to hold the form data
        const formData = new FormData(this.form);
        const jsonObject = {};

        // Convert the form data to a JSON object
        formData.forEach((value, key) => {
            jsonObject[key] = value;
        });

        return fetch(this.commandUrl, {
            method: "POST",
            body: JSON.stringify(jsonObject), // Convert the JSON object to a string
            headers: {
                'Accept': 'text/plain', // for fetch streaming only accept plain text, we won't handle html
                'Content-Type': 'application/json' // Set the content type to JSON
            }
        });
    }
    async processStreamReader(reader) {
        while (true) {
            const result = await reader.read();
            let chunk = this.decoder.decode(result.value);
            console.log(chunk);
            let insert_func = this.output_div.insertAdjacentText;
            let elem = this.output_div;

            // Split the read chunk into sections if needed.
            // Below implementation is not perfect as it expects the CLICK_WEB section markers to be
            // complete and not in separate chunks. However it seems to work fine
            // as long as the generating server yields the CLICK_WEB section in one string as they should be
            // quite small.
            if (chunk.includes('<!-- CLICK_WEB')) {
                // there are one or more click web special sections, use regexp split chunk into parts
                // and process them individually
                let parts = chunk.split(/(<!-- CLICK_WEB [A-Z]+ [A-Z]+ -->)/);
                for (let part of parts) {
                    [elem, insert_func] = this.getInsertFunc(part, elem, insert_func);
                    if (part.startsWith('<!-- ')) {
                        // no not display end section comments.
                        continue;
                    } else {
                        insert_func.call(elem, 'beforeend', part);
                    }
                }
            } else {
                insert_func.call(elem, 'beforeend', chunk);
            }

            if (result.done) {
                break
            }
        }
    }

    getInsertFunc(part, current_elem, current_func) {
        // If we enter new section modify output method accordingly.
        if (part.includes(' START ')) {
            if (part.includes(' HEADER ')) {
                return [this.output_header_div, this.output_header_div.insertAdjacentHTML];
            } else if (part.includes(' FOOTER ')) {
                return [this.output_footer_div, this.output_footer_div.insertAdjacentHTML];
            } else {
                throw new Error("Unknown part:" + part);
            }
        } else if (part.includes(' END ')) {
            // plain text again
            return [this.output_div, this.output_div.insertAdjacentText];
        } else {
            // no change
            return [current_elem, current_func];
        }
    }
}

