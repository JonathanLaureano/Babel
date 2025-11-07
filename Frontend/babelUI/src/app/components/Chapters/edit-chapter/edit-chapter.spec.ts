import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditChapter } from './edit-chapter';

describe('EditChapter', () => {
  let component: EditChapter;
  let fixture: ComponentFixture<EditChapter>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditChapter]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditChapter);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
