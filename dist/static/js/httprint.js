function uploadFile() {
    let photo = document.getElementById("upload-file").files[0];
    let copies = document.getElementById("copies").value;
    let formData = new FormData();

    formData.append("file", photo);
    formData.append("copies", copies);
    var uploadField = document.getElementById("upload-file");
    fetch("/api/upload", {method: "POST", body: formData})
        .then(function(response) {
            return response.json();
        })
        .then(function(reply) {
            if (reply && !reply.error) {
                iziToast.success({
                    title: "DONE!",
                    message: reply.message || "file sent to printer",
                    position: "topCenter",
                    timeout: false,
                    closeOnEscape: true,
                    layout: 2
                });
            } else {
                iziToast.error({
                    title: "ERROR!",
                    message: reply.message || "unable to print file",
                    position: "topCenter",
                    layout: 2
                });
            }
            uploadField.value = null;
        })
        .catch(function(err) {
            console.log(err);
            iziToast.error({
                title: "ERROR!",
                message: "failed to send file",
                position: "topCenter",
                layout: 2
            });
            uploadField.value = null;
        });
}


document.addEventListener("DOMContentLoaded", function(event) {
    let pbutton = document.getElementById("print-btn");
    pbutton.addEventListener("click", function(event) {
        uploadFile();
    });
});
