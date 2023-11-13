import {
    AudioConfig,
    AudioFormatTag,
    AudioInputStream,
    AudioStreamFormat,
    PullAudioInputStream,
    ResultReason,
    SpeechConfig,
    SpeechRecognizer,
} from "microsoft-cognitiveservices-speech-sdk";
const fs = require('node:fs');

const AUDIO_FILE = "7.wav";

const region = "<your_region>";
const key = "<your_subscription_key>";
const LoadArrayFromFile = (filename: string): ArrayBuffer => {
    const fileContents: Buffer = fs.readFileSync(filename);

    const ret = Uint8Array.from(fileContents.slice(44));

    return ret.buffer;
}

const fileBuffer: ArrayBuffer = LoadArrayFromFile(AUDIO_FILE);

// set up cognitive services
const format = AudioStreamFormat.getWaveFormat(8000, 8, 2, AudioFormatTag.MuLaw);
let bytesSent: number = 0;
let p: PullAudioInputStream;

p = AudioInputStream.createPullStream(
    {
        close: () => { return; },
        read: (buffer: ArrayBuffer): number => {
            const copyArray: Uint8Array = new Uint8Array(buffer);
            const start: number = bytesSent;
            const end: number = buffer.byteLength > (fileBuffer.byteLength - bytesSent) ? (fileBuffer.byteLength) : (bytesSent + buffer.byteLength);
            copyArray.set(new Uint8Array(fileBuffer.slice(start, end)));
            bytesSent += (end - start);

            if (bytesSent < buffer.byteLength) {
                setTimeout(() => p.close(), 1000);
            }

            return (end - start);
        },
    },
    format);
    const audioConfig = AudioConfig.fromStreamInput(p);
    const speechConfig = SpeechConfig.fromSubscription(key, region);
    const recognizer = new SpeechRecognizer(speechConfig, audioConfig);

    // handle results
    recognizer.recognized = (_s, event) => {
        console.debug(`(recognized)  Reason: ${ResultReason[event.result.reason]} Text: ${event.result.text}`);
    };
    recognizer.canceled = () => {
        console.error("canceled");
    };

    // start!
    recognizer.startContinuousRecognitionAsync();

