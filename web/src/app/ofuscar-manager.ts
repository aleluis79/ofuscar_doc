import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OfuscarManager {

  URL_API = 'http://localhost:9090/';

  http = inject(HttpClient);
  
  ofuscar(texto: string) : Observable<Ofuscar> {
    return this.http.post<Ofuscar>(this.URL_API + 'ofuscar', { texto });
  }

  desofuscar(texto: Ofuscar) : Observable<Desofuscar> {
    return this.http.post<Desofuscar>(this.URL_API + 'desofuscar', texto);
  }
 
}

export interface Ofuscar {
  texto_ofuscado: string;
  mapeos: any;
}

export interface Desofuscar {
  texto_desofuscado: string;
}
