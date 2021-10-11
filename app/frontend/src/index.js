var ws = null;

const messages = document.createElement('ul');
document.body.appendChild(messages);

const onMessage = (event) =>
{
    const data = event.data;

    if(data == 'reload')
    {
        window.location.reload(false);
        return;
    }

    const messages = document.getElementsByTagName('ul')[0];
    const message = document.createElement('li');
    const content = document.createTextNode(data);
    message.appendChild(content);
    messages.appendChild(message);
};

const onError = (e, b, c) => 
{
    setTimeout(connect, 500);
};

const onOpen = () => 
{
};

function connect() {
  ws = new WebSocket("ws://127.0.0.1:8057");

  ws.onopen = onOpen;
  ws.onclose = onError;
  ws.onerror = onError;
  ws.onmessage = onMessage;
}

connect();