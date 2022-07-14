import base64
from random import choice
from typing import Union, Optional


class BaseApiTTS:
    max_chars: int
    decode_base64: bool = False

    @staticmethod
    def text_len_sanitize(
            text: str,
            max_length: int,
    ) -> list:
        """
        Splits text if it's too long to be a query

        Args:
            text: text to be sanitized
            max_length: maximum length of the query

        Returns:
            Split text as a list
        """
        # Split by comma or dot (else you can lose intonations), if there is non, split by groups of 299 chars
        if '.' in text and all([split_text.__len__() < max_length for split_text in text.split('.')]):
            return text.split('.')

        if ',' in text and all([split_text.__len__() < max_length for split_text in text.split(',')]):
            return text.split(',')

        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    def write_file(
            self,
            output_text: str,
            filepath: str,
    ) -> None:
        """
        Writes and decodes TTS responses in files

        Args:
            output_text: text to be written
            filepath: path/name of the file
        """
        decoded_text = base64.b64decode(output_text) if self.decode_base64 else output_text

        with open(filepath, 'wb') as out:
            out.write(decoded_text)

    def run(
            self,
            text: str,
            filepath: str,
    ) -> None:
        """
        Calls for TTS api and writes audio file

        Args:
            text: text to be voice over
            filepath: path/name of the file

        Returns:

        """
        output_text = ''
        if len(text) > self.max_chars:
            for part in self.text_len_sanitize(text, self.max_chars):
                if part:
                    output_text += self.make_request(part)
        else:
            output_text = self.make_request(text)
        self.write_file(output_text, filepath)


def get_random_voice(
        voices: Union[list, dict],
        key: Optional[str] = None,
) -> str:
    """
    Return random voice from list or dict

    Args:
        voices: list or dict of voices
        key: key of a dict if you are using one

    Returns:
        random voice as a str
    """
    if isinstance(voices, list):
        return choice(voices)
    else:
        return choice(voices[key] if key else list(voices.values())[0])


def audio_length(
        path: str,
) -> float | int:
    """
    Gets the length of the audio file

    Args:
        path: audio file path

    Returns:
        length in seconds as an int
    """
    from mutagen.mp3 import MP3

    try:
        audio = MP3(path)
        return audio.info.length
    except Exception as e:
        import logging

        logger = logging.getLogger('spam_application')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('tts_log', mode='a+', encoding='utf-8')
        logger.addHandler(handler)
        logger.error('Error occurred in audio_length:', e)
        return 0
