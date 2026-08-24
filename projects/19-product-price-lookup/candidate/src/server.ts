import { app } from './app';

const PORT = process.env.PORT ? Number(process.env.PORT) : 3000;

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Product Price Lookup API listening on port ${PORT}`);
});
