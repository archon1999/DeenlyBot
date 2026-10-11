export type CalendarDto = {
  events: {
    id: number;
    date: string;
    hijri_year: number;
    title: string;
    description: string;
    is_estimated: boolean;
  }[];
};
