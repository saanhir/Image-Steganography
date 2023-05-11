import numpy as np
from PIL import Image


class LsbEncryptor:


    def modify_data(self, data, ptext):

        text = str(len(ptext)) + "/" + ptext

        length = len(text)
        cur_index = 0
        max_row = data.shape[0]
        max_col = data.shape[1]
        row = 0
        col = 0
        while cur_index < length:

            character = ord(text[cur_index])
            mask = 0b10000000

            for i in range(8):

                if col >= max_col:
                    col = 0
                    row += 1
                if row >= max_row:
                    return data     # incomplete encoding

                masked = 1 if character & mask > 0 else 0   # target LS bit

                data[row][col][0] = ((data[row][col][0] >> 1) << 1) + masked    # replace last bit with target bit
                mask = mask >> 1

                col += 1

            cur_index += 1

        return data


    def read_data(self, data):

        out_length = ""

        max_row = data.shape[0]
        max_col = data.shape[1]
        row = 0
        col = 0

        # find length
        while True:
            cur_char = 0b00000000
            for _ in range(8):
                if col >= max_col:
                    col = 0
                    row += 1
                if row >= max_row:
                    return None     # ??? incomplete length encoding?

                cur_char <<= 1
                cur_char += (data[row][col][0] & 1)     # yields last bit

                col += 1

            if chr(cur_char) == "/":
                break
            else:
                out_length += chr(cur_char)

        out_length = int(out_length)

        # Decode message
        cur_index = 0
        out_text = ""

        while out_length > cur_index:
            cur_char = 0b00000000
            for _ in range(8):
                if col >= max_col:
                    col = 0
                    row += 1
                if row >= max_row:
                    return out_text     # message takes whole data

                cur_char <<= 1
                cur_char += (data[row][col][0] & 1)  # yields last bit

                col += 1

            out_text += chr(cur_char)
            cur_index += 1


        return out_text


    def encode(self, src, dst, ptext):

        im = Image.open(src)

        data_read = np.asarray(im)
        data_write = data_read.copy()

        data_write = self.modify_data(data_write, ptext)

        image_result = Image.fromarray(data_write)
        image_result.save(dst)

    def decode(self, src):

        im = Image.open(src)
        im_data = np.asarray(im)

        text = self.read_data(im_data)
        return text



