/**
 * The HtmlVideo Strategy is responsible for interfacing between the Video Pinger and an instance of
 * HTML5 video in the DOM.
 */


/**
 * @inheritDoc
 * @constructor
 * @implements {AudioStrategy}
 */
function AudioStrategy(player) {

  /**
   * The HtmlVideo player object to listen to events on.
   * @type {Object}
   * @private
   */
  this.player_ = player;

  /**
   * The ready flag, set when the player is ready to be pinged.
   * @type {boolean}
   * @private
   */
  this.ready_ = false;

  /**
   * The current ad location (preroll, midroll, etc)
   * @type {StrategyInterface.AdPosition|undefined}
   * @private
   */
  this.currentAdPosition_ = undefined;

  /**
   * Tracks if the video was ever started.
   * @type {boolean}
   * @private
   */
  this.videoPlayed_ = false;

  /**
   * The timestamp of when the viewing session is started
   * @type {number|undefined}
   * @private
   */
  this.viewStartTime_ = new Date().getTime();

  /**
   * The timestamp of when the video started
   * @type {number|undefined}
   * @private
   */
  this.videoStartTime_ = undefined;

  // Subscribe to events from the player
  this.subscribeEvents_();
};

/**
 * Enum for the content type.
 * @enum {string}
 */
AudioStrategy.ContentType = {
  AD: 'ad',
  CONTENT: 'ct'
};


/**
 * Enum for the ad position.
 * @enum {string}
 */
AudioStrategy.AdPosition = {
  PREROLL: 'a1',
  MIDROLL: 'a2',
  POSTROLL: 'a3',
  OVERLAY: 'a4',
  SPECIAL: 'a5'
};


/**
 * Enum for the video state.
 * @enum {string}
 */
AudioStrategy.VideoState = {
  UNPLAYED: 's1',
  PLAYED: 's2',
  STOPPED: 's3',
  COMPLETED: 's4'
};


/**
 * Subscribes to message bus events.
 * @private
 */
AudioStrategy.prototype.subscribeEvents_ = function() {
  // If already in the ready state, call onPlaybackReady_
  if (this.player_.readyState > 2) {
    this.onPlaybackReady_();
  }

  // If already in the playing state, call onVideoPlay_
  if (this.player_.currentTime > 0 &&
      !this.player_.paused && !this.player_.ended) {
    this.onVideoPlay_();
  }

  // Listen for the playback ready event before sending pings
  this.player_.addEventListener('canplay',
    this.bind_(this.onPlaybackReady_, this));

  // Event is triggered when the video is started playing
  this.player_.addEventListener('playing',
    this.bind_(this.onVideoPlay_, this));
};


/**
 * Proxy the function through the context provided.
 * @param {Function} fn The function to invoke.
 * @param {Object} context The context to call the function under.
 * @return {Function} The function to bind wrapped in an anonymous proxy function.
 * @private
 */
AudioStrategy.prototype.bind_ = function(fn, context) {
  return function(){
    fn.call(context);
  };
};


/**
 * Handle when the video is ready for playback.
 * @private
 */
AudioStrategy.prototype.onPlaybackReady_ = function() {
  this.ready_ = true;
};


/**
 * Handle when the video is played.
 * @private
 */
AudioStrategy.prototype.onVideoPlay_ = function() {
  this.videoStartTime_ = new Date().getTime();
  this.videoPlayed_ = true;
};


/**
 * Indicates if the video strategy is ready for pinging.
 * Note: Pings should only be sent after this reads true.
 * @return {boolean} The ready state of the strategy.
 */
AudioStrategy.prototype.isReady = function() {
  return this.ready_;
};


/**
 * Gets the human readable video title.
 * @return {string} The video title.
 */
AudioStrategy.prototype.getTitle = function() {
  return (this.player_.attributes['title'] && this.player_.attributes['title'].value) || '';
};


/**
 * Gets the video path.
 * Note: this should be the playable video path if available.
 * @return {string} The video path.
 */
AudioStrategy.prototype.getVideoPath = function() {
  var item = this.player_['currentSrc'];
  return item || '';
};


/**
 * Gets the type of video playing.
 * @return {StrategyInterface.ContentType} The type of content (ad or ct).
 */
AudioStrategy.prototype.getContentType = function() {
  return AudioStrategy.ContentType.CONTENT;
};


/**
 * Gets the ad position.
 * @return {StrategyInterface.AdPosition|string} The ad position
 * from a1 (pre-roll), a2 (mid-roll), a3 (post-roll),
 * a4 (overlay), or a5 (special).
 */
AudioStrategy.prototype.getAdPosition = function() {
  return '';
};


/**
 * Gets the total duration of the video.
 * @return {number} The total duration time in milliseconds.
 */
AudioStrategy.prototype.getTotalDuration = function() {
  var d = this.player_['duration'];
  return this.getTimeInSeconds_(d);
};


/**
 * Gets the current state of the video.
 * @return {string} The current video state. {@link StrategyInterface.VideoState}
 */
AudioStrategy.prototype.getState = function() {
  if (!this.videoPlayed_) {
    return AudioStrategy.VideoState.UNPLAYED;
  }

  if (this.player_.ended) {
    return AudioStrategy.VideoState.COMPLETED;
  }

  if (this.player_.paused) {
    return AudioStrategy.VideoState.STOPPED;
  }

  return AudioStrategy.VideoState.PLAYED;
};


/**
 * Calculates the time elapsed since the timestamp.
 * @param  {number|undefined} timestamp The timestamp to calculate the elapsed time against.
 * @return {number} The elapsed time since timestamp.
 * @private
 */
AudioStrategy.prototype.timeElapsed_ = function(timestamp) {
  if (timestamp === undefined) {
    return 0;
  }
  var t = new Date().getTime();
  return t - timestamp;
};


/**
 * Handles an embed code change (aka video/audio changing).
 * @private
 */
AudioStrategy.prototype.onEmbedCodeChanged_ = function() {
  this.currentAdPosition_ = undefined;
  this.adStartTime_ = undefined;
};


/**
 * Gets the current play time of the video.
 * @return {number} The current play time in milliseconds.
 */
AudioStrategy.prototype.getCurrentPlayTime = function() {
  var pt = this.player_['currentTime'];
  return this.getTimeInSeconds_(pt);
};


/**
 * Gets the current bitrate of the video.
 * @return {number} The current bitrate in kbps.
 */
AudioStrategy.prototype.getBitrate = function() {
  return -1;
};


/**
 * Gets the thumbnail of the video.
 * @return {string} The [absolute] path to the thumbnail.
 */
AudioStrategy.prototype.getThumbnailPath = function() {
  return (this.player_.attributes['poster'] && this.player_.attributes['poster'].value) || '';
};


/**
 * Gets the video player type.
 * @return {string} The name of the strategy
 */
AudioStrategy.prototype.getPlayerType = function() {};


/**
 * Gets the time since start of viewing.
 * @return {number} The time since viewing started in milliseconds.
 */
AudioStrategy.prototype.getViewStartTime = function() {
  if (isNaN(this.viewStartTime_)) {
    return 0;
  }

  return this.timeElapsed_(this.viewStartTime_);
};


/**
 * Gets the time since start of viewing for users in a play state -- regardless of current state.
 * @return {number} The time since viewing started in milliseconds.
 */
AudioStrategy.prototype.getViewPlayTime = function() {
  if (this.videoPlayed_) {
    return this.timeElapsed_(this.viewStartTime_);
  }

  return -1;
};


/**
 * Gets the time since play start for users who saw an ad -- regardless of current state.
 * @return {number} The time since viewing started in milliseconds.
 */
AudioStrategy.prototype.getViewAdPlayTime = function() {
  return -1;
};


/**
 * Returns the time in seconds, or -1 if not a number/
 * @param  {number} t Time to be converted from ms to seconds.
 * @return {number} Time in seconds or -1 if not a valid value.
 */
AudioStrategy.prototype.getTimeInSeconds_ = function(t) {
  return ((t === -1 || isNaN(t)) ? -1 : t * 1000);
};


/**
 * Verifies that the given player belongs to this strategy. Used for a
 * greedy search of the matching strategy for a given element or object.
 * @param {Object} player A pointer to the player being tracked.
 * @return {boolean} If the strategy can handle this type of object.
 */
AudioStrategy.verify = function(player) {
  return player instanceof HTMLElement &&
    player.nodeName === 'AUDIO';
};
