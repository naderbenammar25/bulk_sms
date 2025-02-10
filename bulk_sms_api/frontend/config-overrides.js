const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');

module.exports = function override(config, env) {
  config.plugins.push(
    new BundleTracker({ path: path.join(__dirname, 'build'), filename: 'webpack-stats.json' })
  );
  return config;
};