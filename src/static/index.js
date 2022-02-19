function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}


function setImagesUrl(imagesurl){
    if (existingFiles.length == 0)
    {existingFiles = imagesurl;
    console.log(existingFiles.length);
    setdzobjconfig();}
   
}

function trytest() {
    // console.log(form.item_id.value);
    // fileList = new Array();
    // fetch("/activity/confirm/images", {
    //     method: "POST",
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ title: form.title.value, content: form.content.value, group_id: form.group_id.value, item_id: form.item_id.value })
    // }).then((_res) => {
        // console.log(JSON.stringify(_res))
        // console.log(14)
        // window.location.href = "/activities/edit/14";
        // var $ul = $('ul#images').empty();  // the ul where images end up....
        // var images = data[0].images.split(',');
        // $.each(images, function (idx, img) {
        //     $ul.append('<li><a><img src="https://mdbcdn.b-cdn.net/img/new/standard/city/042.webp" height="72" width="72" alt=""/></a></li>');
        // })
       
    // });
    // confirm_image
   
    if (Object.keys(fileList).length > 0 && isTempAdded){
        console.log("object length->" + Object.keys(fileList).length );
    var $ul = $('#card_images').empty(); 
    $.each(Object.keys(fileList), function (key, val) {
        // console.log(fileList[val].fid);
       
        var temp = '';
        if (fileList[val].fid.includes('http'))
            temp = fileList[val].fid;
        else
           temp = "/static/uploads/"+ fileList[val].fid;
        $ul.append(' <div class="card"><img class="card-img-top" src="' + temp + '" height="200" width="200" alt=""/></div>');
        
    });
} else{
        $('#card_images').empty();
}
    console.log(fileList)
}

$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

   
}); 




Dropzone.autoDiscover = false;
fileList = new Array();
var existingFiles = [
    // {
    //     name: "leave.jpeg", size: 12345678, dataURL: "https://images.unsplash.com/photo-1471879832106-c7ab9e0cee23?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxleHBsb3JlLWZlZWR8Mnx8fGVufDB8fHx8&w=1000&q=80", accepted: true
    // },
    // { name: "Filename 2.pdf", size: 12345678 },
    // { name: "Filename 3.pdf", size: 12345678 },
    // { name: "Filename 4.pdf", size: 12345678 },
    // { name: "Filename 5.pdf", size: 12345678 }
];
isTempAdded = false;
var dzObj;
$(document).ready(function () {

   
   
    $("#id_dropzone").dropzone({
        addRemoveLinks: true,
        clickable: true,
        // dictRemoveFileConfirmation: "Are you sure you want to remove this File?", 
        maxFiles: 2000,
        init: function () {
             dzObj = this;
            console.log('start dropzone')
            fileList = new Array();
            this.on("complete", function (file) {
                $(".dz-remove").html("<div><span class='fa fa-trash text-danger' style='font-size: 1.5em'></span></div>");
            });

           
        },
        success: function (file, serverFilePath) {
        isTempAdded = true;
           fileList[file.name] = { "fid": serverFilePath };
           console.log(fileList);
            console.log(file.dataURL);
        },
        removedfile: function (file) {
            console.log(fileList);
            console.log(fileList[file.name].fid);
            file.previewElement.remove();

            deleteActivity(file.name, fileList[file.name].fid);
            delete fileList[file.name]; 
           
          },
        error: function (file, response) {
            console.log("Erro");
            console.log(response);
        },
        // complete: function (file) {
        //     console.log("Complete");
        // }
    });

    // dzObj.on("sending", function (file, xhr, formData) {
    //     formData.append("full_path", file.fullPath);
    //     // console.log(formData.get("full_path"));
    // });

   
})

function setdzobjconfig() {
    existingFiles.forEach(myFunction);
    function myFunction(item) {
        // console.log(item.dataURL)
        console.log(item.name)
        dzObj.files.push(item);
        dzObj.emit("addedfile", item);
        dzObj.createThumbnailFromUrl(item, dzObj.options.thumbnailWidth, dzObj.options.thumbnailHeight, dzObj.options.thumbnailMethod, true, function (dataUrl) {
            dzObj.emit("thumbnail", item, dataUrl);
        }, "anonymous");
        dzObj.emit("success", item, item.dataURL);
        dzObj.emit("complete", item);
    }

    
}

function deleteActivity(filename, filePath) {
    fetch("/delete", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: filename, filePath: filePath})
    }).then((_res) => {
        // console.log(JSON.stringify(_res))
        // window.location.href = "/";
    });
}

function getVideoId() {

    var input = document.getElementById("video").value;

    fetch("/video/id", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: input })
    }).then(response => response.json())
        .then(data => {
            // "https://www.youtube.com/embed/ivGkoZ2E-sw" 
            var $ul = $('#youtube_preview').empty(); 
            $ul.append(' <iframe width="200" height="200" src="https://www.youtube.com/embed/' + data['data'] + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>');
            console.log(data['data']);
        });
}
