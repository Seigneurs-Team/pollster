new Vue({
  ...
  apolloProvider: createProvider({
    httpEndpoint: 'http://localhost:8000/',
    wsEndpoint: null,
  }),
  ...
})