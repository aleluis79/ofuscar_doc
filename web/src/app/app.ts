import { Component, effect, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { Ofuscar, OfuscarManager } from './ofuscar-manager';
import { JsonPipe } from '@angular/common';
import { SwitchMode } from './switch-mode/switch-mode';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, JsonPipe, SwitchMode],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('web');

  texto_a_ofuscar = signal('');
  texto_ofuscado = signal('');
  texto_desofuscado = signal('');
  mapeos = signal('');

  ofuscarManager = inject(OfuscarManager);

  ef = effect(() => {
    if (!this.texto_a_ofuscar()) {
      this.mapeos.set('')
    }
  })

  ofuscar(texto: string) {
    this.texto_desofuscado.set('');
    this.ofuscarManager.ofuscar(texto).subscribe((ofuscado) => {
      this.texto_ofuscado.set(ofuscado.texto_ofuscado);
      this.mapeos.set(ofuscado.mapeos);
    });
  }

  desofuscar() {   
    const request : Ofuscar = {
      texto_ofuscado: this.texto_ofuscado(),
      mapeos: this.mapeos()
    }
    this.ofuscarManager.desofuscar(request).subscribe((desofuscado) => {
      this.texto_desofuscado.set(desofuscado.texto_desofuscado);
    });
  }

  
}
