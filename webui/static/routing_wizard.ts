document.addEventListener("DOMContentLoaded", () => {
    const data_area = document.getElementById("data-area") as HTMLTextAreaElement;

    const data_set_buttons: NodeListOf<Element> = document.querySelectorAll(".load-data-set");
    data_set_buttons.forEach((element: Element) => {
        element.addEventListener("click", (e: Event) => {
            const target = e.target as HTMLElement;
            fetch(`/load-data/${target.id}`)
                .then(res => res.json())
                .then((data) => {
                    data_area.value = data['data'];
                })
        })
    })

    const reader = new FileReader();
    reader.onload = (event) => {
        const content = event.target?.result;
        if (typeof content === 'string') {
            data_area.value = content;
        } else {
            console.error("File content is not a string.");
        }
    };

    const file_upload = document.getElementById("file") as HTMLInputElement;
    file_upload.addEventListener("change", (event: Event) => {
        const input = event.target as HTMLInputElement;
        if (!input.files || input.files.length === 0) {
            console.error("No file selected");
            return;
        }
        reader.readAsText(input.files[0]);
    })


    const submit_button = document.getElementById("submit-data") as HTMLButtonElement;
    submit_button.addEventListener("click", (event: Event) => {
        const data = {"data": data_area.value}
        fetch('/submit-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(resp => resp.json())
        .then(data => {

            const image_div = document.getElementById("image-location");
            const image = document.createElement("img");
            image.src = data['data'];
            image.alt = "Plot image";
            image.id = "plot-image";

            image_div.appendChild(image);


        })
        .catch(error => {console.error(error);
        });
    })




})
