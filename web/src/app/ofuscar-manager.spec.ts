import { TestBed } from '@angular/core/testing';

import { OfuscarManager } from './ofuscar-manager';

describe('OfuscarManager', () => {
  let service: OfuscarManager;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(OfuscarManager);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
