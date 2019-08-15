function uploadFile() {
    let photo = document.getElementById("upload-file").files[0];
    let copies = document.getElementById('copies').value;
    let formData = new FormData();

    formData.append("file", photo);
    formData.append("copies", copies);
    var uploadField = document.getElementById('upload-file');
    fetch("/api/upload", {method: "POST", body: formData})
        .then(function(response) {
            return response.json();
        })
        .then(function(reply) {
            if (reply && !reply.error) {
                iziToast.success({
                    title: "DONE!",
                    message: reply.message,
                    position: 'topCenter',
                    timeout: false,
                    closeOnEscape: true,
                    layout: 2
                });
            } else {
                iziToast.error({
                    title: "ERROR!",
                    message: reply.message,
                    position: 'topCenter',
                    layout: 2
                });
            }
            uploadField.value = null;
        })
        .catch(function(err) {
            iziToast.error({
                title: "ERROR!",
                message: "failed to send file",
                position: 'topCenter',
                layout: 2
            });
            uploadField.value = null;
        });
}
