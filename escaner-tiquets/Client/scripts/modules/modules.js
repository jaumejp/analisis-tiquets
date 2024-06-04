import { exampleJson, loadingJson, apiUrl } from './constants.js'

export function textareaText(textarea, text) {
    const jsonData = JSON.parse(text)
    const formattedJsonString = JSON.stringify(jsonData, null, 4)

    textarea.textContent = formattedJsonString
}

export function audio() {

    const audioContent = document.querySelector('#audioBase64').innerHTML

    if (audioContent == '') {
        alert("Procesa primer un tiquet.")
        return
    }

    // Decodificar l'audio en base64
    const binaryString = window.atob(audioContent);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: "audio/mpeg" });

    // Objecte reproductor d'audio en el navegador
    const audio = new Audio();
    audio.src = URL.createObjectURL(blob);

    // Reproduir audio
    audio.play();
}

export function addEvents() {
    
    const pdfBtn = document.querySelector('#proccesPdf')
    const img = document.querySelector('#ticket_img')
    const inputsContainer = document.querySelector('#inputs_container')
    const resetBtn = document.querySelector('#resetBtn')
    const textarea = document.querySelector('.pdf-info')
    const userId = document.querySelector('#userId')
    const fileUploader = document.querySelector('#fileUploader')
    const audioBase64 = document.querySelector('#audioBase64')
    const audioBtn = document.querySelector('#audioBtn')

    resetBtn.addEventListener("click", (e) => {
        e.preventDefault()
        img.src = ''
        userId.value = ''
        inputsContainer.classList.remove('d-none')
        fileUploader.value = ''
        textareaText(textarea, exampleJson)
        audioBase64.innerHTML = ''
        audioBtn.classList.add('btn-disabled')
    })

    pdfBtn.addEventListener("click", (e) => {
        e.preventDefault();
    
        const pdfFile = fileUploader.files[0];
        
        if (pdfFile == undefined || userId.value == '') {
            alert("Selecciona un pdf i introdueix un id d'usuari")
            return;
        }

        // if (img.src != 'http://127.0.0.1:5500/Client/index.html') {
        //     alert("Ja s'ha executat el procés amb aquest pdf.\nSi vols tornar a provar, prem el botó de resetejar.")
        //     return
        // }
    
        textareaText(textarea, loadingJson);
        
        // Llegim el pdf en base64 per pasar-lo al servidor
        const reader = new FileReader();
        reader.readAsDataURL(pdfFile);
        
        // readAsDataURL es una funcio asíncrona
        reader.onload = () => {
            const base64 = reader.result.split(',');
            const base64pdf = base64[1];
            const base64extension = base64[0].split('/')[1].split(';')[0];

            const endpoint = `${apiUrl}/pdf/${userId.value}`;
    
            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    pdfData: base64pdf,
                    extension: base64extension 
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error al enviar el pdf al servidor");
                }
                return response.json();
            })
            .then(data => {

                inputsContainer.classList.add('d-none');
                
                const { image, ticket, audio } = data; 

                audioBase64.innerHTML = audio
                audioBtn.classList.remove('btn-disabled')
                img.src = `data:image/jpeg;base64, ${image}`;

                const jsonString = JSON.stringify(ticket)
                textareaText(textarea, jsonString);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        };
    });
}