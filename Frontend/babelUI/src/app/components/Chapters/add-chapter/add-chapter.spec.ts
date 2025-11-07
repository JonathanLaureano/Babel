import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddChapter } from './add-chapter';

describe('AddChapter', () => {
  let component: AddChapter;
  let fixture: ComponentFixture<AddChapter>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddChapter]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddChapter);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
