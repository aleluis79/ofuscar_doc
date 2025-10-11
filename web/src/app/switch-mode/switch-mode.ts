import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-switch-mode',
  imports: [],
  templateUrl: './switch-mode.html',
  styleUrl: './switch-mode.css'
})
export class SwitchMode  implements OnInit {
  theme: 'light' | 'dark' | 'auto' = 'auto';

  ngOnInit() {
    // Leer el modo guardado
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | 'auto' | null;
    this.theme = saved ?? 'auto';
    this.applyTheme();
  }

  toggleTheme() {
    // Rotar entre los tres modos
    this.theme = this.theme === 'auto' ? 'light' : this.theme === 'light' ? 'dark' : 'auto';
    localStorage.setItem('theme', this.theme);
    this.applyTheme();
  }

  applyTheme() {
    const html = document.documentElement;
    html.classList.remove('dark');

    if (this.theme === 'dark') {
      html.classList.add('dark');
    } else if (this.theme === 'auto') {
      // Detecta preferencia del sistema
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) html.classList.add('dark');
    }
  }
}
