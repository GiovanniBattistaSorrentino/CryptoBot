# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.



class UserProfile:
    def __init__(self, id: int = 0, nome_utente: str = None, cripto_tracciate: str = None):
        self.id = id
        self.nome_utente = nome_utente
        self.cripto_tracciate = cripto_tracciate

    # Getter
    def getId(self):
        return self.id
    def getNome_utente(self):
        return self.nome_utente
    def getCripto_tracciate(self):
        return self.cripto_tracciate

    # Setter
    def setNome_utente(self, nome_utente):
        self.nome_utente = nome_utente
    def setCripto_tracciate(self, cripto_tracciate):
        self.cripto_tracciate = cripto_tracciate


    #metodi sovrascritti
    def __str__(self):
        return f"id: {self.id}, " \
               f"nome_utente: {self.nome_utente}, " \
               f"cripto_tracciate: {self.cripto_tracciate}"

    # Metodi sovrascritti
    def __eq__(self, o: object) -> bool:
        if isinstance(o, UserProfile):
            return self.id == o.id and self.nome_utente == o.nome_utente and self.cripto_tracciate == o.cripto_tracciate
