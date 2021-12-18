function genreateGUID()
{
    function b(a){return a?(a^Math.random()*16>>a/4).toString(16):([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,b)};
    return b();
}

function capitalizeFirstLetter(str)
{
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function makeDiv(type, attributes)
{
    if(typeof type == 'object')
    {
        attributes = type;
        type = 'div';
    }

    const el = document.createElement(type);

    for(const attr in attributes)
    {
        let value = attributes[attr];

        if(attr == 'class' || attr == 'classes' || attr == 'classList')
        {
            if(typeof value == "string")
            {
                value = value.split(' ');
            }

            for(let className of value)
            {
                className = className.trim()
                className && el.classList.add(className.trim());
            }
        }
        if(attr == 'style')
        {
            for(const prop in value)
            {
                el.style[prop] = value[prop];
            }
        }
        else if(attr == 'parent')
        {
            value.appendChild(el);
        }
        else
        {
            el[attr] = value;
        }
    }

    return el;
}

function onUploadFile(input, callback, allowMultipleFiles = true)
{
    if(allowMultipleFiles)
    {
        input.multiple = 'multiple';
        input.name = 'files[]';
    }
    else
    {
        delete input.multiple;
        input.name = 'file';
    }

    input.addEventListener('change', (e) => 
    {
        if(!e.target.files) return;

        for(const file of e.target.files)
        {
            if (!file)
            {
                continue;
            }

            const reader = new FileReader();
            reader.onload = (e) => 
            {
                const contents = e.target.result;
                callback(contents, file.name);
            };
            reader.readAsDataURL(file);

            if(!allowMultipleFiles)
            {
                break;
            }
        }
    }, false);
}

function downloadImage(img, name)
{
    let extension = '.png'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    if(img.src.startsWith('data:'))
    {
        const index = img.src.indexOf(';');
        if(index > 0)
        {
            extension = '.' + img.src.substring(5, index);
        }
    }

    const tag = document.createElement('a');
    tag.href = img.src;
    tag.download = name + extension;
    document.body.appendChild(tag);
    tag.click();
    document.body.removeChild(tag);
}

function expandImage(img, name)
{
    const expandedDiv = makeDiv('div', {
        parent: document.body,
        class: 'expanded',
    });

    const close = () => 
    {
        expandedDiv.remove();
    };

    const backgroundDiv = makeDiv('div', {
        parent: expandedDiv,
        class: 'background',
        onclick: close
    });

    const centerDiv = makeDiv('div', {
        parent: expandedDiv,
        class: 'center',
    });

    const imgDiv = makeDiv('img', {
        parent: centerDiv,
        class: 'image',
        src: img.src
    });

    const buttonsDiv = makeDiv('div', {
        parent: centerDiv,
        class: 'buttons',
    });

    const downloadDiv = makeDiv('div', {
        parent: buttonsDiv,
        class: 'button download fas fa-download',
        onclick: () => downloadImage(img, name)
    });

    const closeDiv = makeDiv('div', {
        parent: buttonsDiv,
        class: 'button close fas fa-times',
        onclick: close
    });
}

function downloadableImage(img, name = 'image')
{
    const downloadable = makeDiv('div', {
        parent: img.parentNode,
        class: 'downloadable',
    });

    downloadable.appendChild(img);

    const buttons = makeDiv('div', {
        parent: downloadable,
        class: 'buttons',
    });

    const download = makeDiv('div', {
        parent: buttons,
        class: 'button download fas fa-download',
        onclick: () => downloadImage(img, name)
    });

    const expand = makeDiv('div', {
        parent: buttons,
        class: 'button expand fas fa-expand-arrows-alt',
        onclick: () => expandImage(img, name)
    });

}

function base64toBlob(base64Data, contentType) {
    contentType = contentType || '';
    var sliceSize = 1024;
    var byteCharacters = atob(base64Data);
    var bytesLength = byteCharacters.length;
    var slicesCount = Math.ceil(bytesLength / sliceSize);
    var byteArrays = new Array(slicesCount);

    for (var sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        var begin = sliceIndex * sliceSize;
        var end = Math.min(begin + sliceSize, bytesLength);

        var bytes = new Array(end - begin);
        for (var offset = begin, i = 0; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    return new Blob(byteArrays, { type: contentType });
}

function imageBase64ToUrl(base64, contentType)
{
    const url = URL.createObjectURL(base64toBlob(base64, contentType));
    return url;
}