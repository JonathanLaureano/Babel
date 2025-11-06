import { Routes } from '@angular/router';
import { Homepage } from './components/General/homepage/homepage';
import { AllSeries } from './components/Series/all-series/all-series';
import { SeriesPage } from './components/Series/series-page/series-page';
import { ChapterPage } from './components/Series/chapter-page/chapter-page';
import { Discord } from './components/General/discord/discord';
import { Login } from './components/Users/login/login';
import { Register } from './components/Users/register/register';
import { Profile } from './components/Users/profile/profile';

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