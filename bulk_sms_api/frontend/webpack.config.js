const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  // Autres configurations de Webpack
  plugins: [
    new BundleTracker({ path: __dirname, filename: 'build/webpack-stats.json' }),
  ],
};