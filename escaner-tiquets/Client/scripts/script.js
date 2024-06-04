import { textareaText, addEvents, audio } from './modules/modules.js'
import { exampleJson } from './modules/constants.js'

document.addEventListener('DOMContentLoaded', () => {

    const textarea = document.querySelector('.pdf-info');   
    const audioBtn = document.querySelector('#audioBtn')

    textareaText(textarea, exampleJson)

    addEvents()

    audioBtn.addEventListener("click", audio)
});
