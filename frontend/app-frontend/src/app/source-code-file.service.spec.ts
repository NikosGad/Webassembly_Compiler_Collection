import { TestBed } from '@angular/core/testing';

import { SourceCodeFileService } from './source-code-file.service';

describe('SourceCodeFileService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: SourceCodeFileService = TestBed.get(SourceCodeFileService);
    expect(service).toBeTruthy();
  });
});
