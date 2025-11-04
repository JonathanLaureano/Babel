import { Routes } from '@angular/router';
import { Homepage } from './components/homepage/homepage';
import { AllSeries } from './components/all-series/all-series';
import { SeriesPage } from './components/series-page/series-page';
import { ChapterPage } from './components/chapter-page/chapter-page';
import { Discord } from './components/discord/discord';
import { Login } from './components/login/login';
import { Register } from './components/register/register';
import { Profile } from './components/profile/profile';

export const routes: Routes = [
  { path: '', component: Homepage },
  { path: 'series', component: AllSeries },
  { path: 'series/:id', component: SeriesPage },
  { path: 'series/:id/chapter/:chapterId', component: ChapterPage },
  { path: 'discord', component: Discord },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'profile', component: Profile }
];