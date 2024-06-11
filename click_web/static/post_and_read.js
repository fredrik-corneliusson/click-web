let REQUEST_RUNNING = false;

function postAndRead(commandUrl) {
    if (REQUEST_RUNNING) {
        return false;
    }

    const input_form = document.getElementById("inputform");
    const submit_btn = document.getElementById("submit_btn");

    try {
        REQUEST_RUNNING = true;
        submit_btn.disabled = true;
        const runner = new ExecuteAndProcessOutput(input_form, commandUrl);
        runner.run();
    } catch (e) {
        console.error(e);
    } finally {
        return false;
    }
}

class ExecuteAndProcessOutput {
    constructor(form, commandPath) {
        this.form = form;
        this.commandUrl = commandPath;
        this.decoder = new TextDecoder('utf-8');
        this.output_header_div = document.getElementById("output-header");
        this.output_wrapper_div = document.getElementById("output-wrapper");
        this.output_div = document.getElementById("output");
        this.output_footer_div = document.getElementById("output-footer");
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
        const submit_btn = document.getElementById("submit_btn");
        this.post(this.commandUrl)
            .then(response => {
                this.form.disabled = true;
                const reader = response.body.getReader();
                return this.processStreamReader(reader);
            })
            .then(_ => {
                REQUEST_RUNNING = false;
                submit_btn.disabled = false;
            })
            .catch(error => {
                console.error(error);
                REQUEST_RUNNING = false;
                submit_btn.disabled = false;
            });
    }

    post() {
        console.log("Posting to " + this.commandUrl);

        const formData = new FormData(this.form);
        const jsonObject = {};

        // Convert the form data to a JSON object
        formData.forEach((value, key) => {
            if (jsonObject[key]) {
                // If key already exists, convert to array and merge values
                if (Array.isArray(jsonObject[key])) {
                    jsonObject[key].push(value);
                } else {
                    jsonObject[key] = [jsonObject[key], value];
                }
            } else {
                jsonObject[key] = value;
            }
        });

        return fetch(this.commandUrl, {
            method: "POST",
            body: JSON.stringify(jsonObject),
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
    }


    async processStreamReader(reader) {
        let buffer = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += this.decoder.decode(value, { stream: true });

            let startIndex = 0;
            let endIndex;
            while ((endIndex = buffer.indexOf('\n', startIndex)) > -1) {
                const jsonString = buffer.slice(startIndex, endIndex).trim().replace(/^\[/, '').replace(/[\n,]$/, '');
                startIndex = endIndex + 1;
                if (jsonString) {
                    try {
                        const jsonMessage = JSON.parse(jsonString);
                        this.processJsonMessage(jsonMessage);
                    } catch (e) {
                        console.error('Failed to parse JSON:', jsonString, e);
                    }
                }
            }
            buffer = buffer.slice(startIndex);
        }
    }

    processJsonMessage(jsonMessage) {
        let elem;
        switch (jsonMessage.status) {
            case 'started':
                elem = this.output_header_div;
                break;
            case 'running':
                elem = this.output_div;
                break;
            case 'completed':
                elem = this.output_footer_div;
                break;
            case 'error':
                elem = this.output_footer_div;
                break;
            default:
                console.error('Unknown status:', jsonMessage.status);
                return;
        }
        elem.insertAdjacentText('beforeend', jsonMessage.message + '\n');
    }
}
