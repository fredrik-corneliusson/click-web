const formid = "inputform";

function post_and_read() {

    var url = document.getElementById(formid).action;
    fetch(url, {
        method: "POST",
        body: new FormData(document.getElementById(formid)),
    }).then(function(response) {
        var reader = response.body.getReader();
        var decoder = new TextDecoder();
        var output = "";
        var output_div = document.getElementById("output")

        function read() {
            return reader.read().then(function(result) {
                output += decoder.decode(result.value);

                if (!result.done) {
                    output_div.innerHTML = output;
                    return read();
                }

            })
        }

        return read();
    });

    return false;
}


