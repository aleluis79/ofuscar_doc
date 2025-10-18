import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class OfuscarManager {

  http = inject(HttpClient);
  
  ofuscar(texto: string, motor?: string) : Observable<Ofuscar> {
    return this.http.post<Ofuscar>(environment.URL_API + '/ofuscar', { texto, motor});
  }

  desofuscar(texto: Ofuscar) : Observable<Desofuscar> {
    return this.http.post<Desofuscar>(environment.URL_API + '/desofuscar', texto);
  }
 
}

export interface Ofuscar {
  texto_ofuscado: string;
  mapeos: any;
}

export interface Desofuscar {
  texto_desofuscado: string;
}
