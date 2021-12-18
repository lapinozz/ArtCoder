var ws = null;
const app = new App();

function sendMessage(event, data = {})
{
    if(!ws)
    {
        return false;
    }

    if(typeof event == 'string')
    {
        data.event = event;
    }

    str = JSON.stringify(data);

    console.log('sending:', str);
    ws.send(str);
    
    return true;
}

function disconnect()
{
    console.error('Disconnected');

    if(ws)
    {
        ws.onopen = null;
        ws.onclose = null;
        ws.onerror = null;
        ws.onmessage = null;
    }

    ws = null;
}

const onMessage = (msg) =>
{
    const data = JSON.parse(msg.data);

    const event = data.event;
    //console.log(data)
    console.log('received:', event)

    if(event == 'reload')
    {
        window.location.reload(false);
        return;
    }

    app.trigger(event, data[event]);
};

const onError = () => 
{
    disconnect();
    app.onConnectionError();
};

const onOpen = () => 
{
    console.log('Connected');

    const sessionId = localStorage.getItem('session-id') || genreateGUID();
    localStorage.setItem('session-id', sessionId);

    sendMessage('sessionId', {id: sessionId});

    app.onConnectionOpen();
};

function connect() {
  ws = new WebSocket("ws://127.0.0.1:8057");

  ws.onopen = onOpen;
  ws.onclose = onError;
  ws.onerror = onError;
  ws.onmessage = onMessage;
}

setInterval(() => 
{
    if(!ws)
    {
        console.error('failed to connect');
        connect();
    }
}, 1000);

connect();