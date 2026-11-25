#!/usr/bin/env python3
"""
Leitura de entradas individuais de um .zip remoto via HTTP Range, sem baixar o pacote inteiro.
Usado para os pacotes por UF de 2022 (cdn.tse.jus.br/.../arqurnatot/bu_imgbu_logjez_rdv_vscmr_2022_<t>_<UF>.zip),
que contem BU, imagem do BU, RDV, assinaturas e logs juntos (centenas de MB por UF).
"""
import io
import time
import urllib.request


class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url, bloco=1 << 20):
        self.url, self.pos, self.bloco = url, 0, bloco
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "pesquisa-academica"})
        with urllib.request.urlopen(req, timeout=60) as r:
            self.size = int(r.headers["Content-Length"])
        self._cache = {}

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def _range(self, a, b, tries=6):
        last = None
        for k in range(tries):
            try:
                req = urllib.request.Request(self.url, headers={"Range": f"bytes={a}-{b}",
                                                                "User-Agent": "pesquisa-academica"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read()
            except Exception as e:
                last = e
                time.sleep(1.5 * 2 ** k)
        raise last

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        data = self._range(self.pos, self.pos + n - 1)
        self.pos += len(data)
        return data

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)
