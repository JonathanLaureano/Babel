import { Routes } from '@angular/router';
import { SeriesListComponent } from './components/series-list/series-list.component';
import { SeriesDetailComponent } from './components/series-detail/series-detail.component';
import { ChapterReaderComponent } from './components/chapter-reader/chapter-reader.component';

export const routes: Routes = [
  { path: '', component: SeriesListComponent },
  { path: 'series/:id', component: SeriesDetailComponent },
  { path: 'chapter/:id', component: ChapterReaderComponent },
];
