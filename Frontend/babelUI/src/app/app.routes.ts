import { Routes } from '@angular/router';
import { Homepage } from './components/homepage/homepage';
import { AllSeries } from './components/all-series/all-series';
import { SeriesPage } from './components/series-page/series-page';
import { ChapterPage } from './components/chapter-page/chapter-page';
import { Discord } from './components/discord/discord';

export const routes: Routes = [
  { path: '', component: Homepage },
  { path: 'series', component: AllSeries },
  { path: 'series/:id', component: SeriesPage },
  { path: 'series/:id/chapter/:chapterId', component: ChapterPage },
  { path: 'discord', component: Discord }
];