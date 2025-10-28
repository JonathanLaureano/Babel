import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';

import { ChapterReaderComponent } from './chapter-reader.component';

describe('ChapterReaderComponent', () => {
  let component: ChapterReaderComponent;
  let fixture: ComponentFixture<ChapterReaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChapterReaderComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([])
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChapterReaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
