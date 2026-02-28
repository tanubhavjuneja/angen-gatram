/**
 * Google Analytics tag for NPR Stations
 * Tag Version  : 000020
 * Publish ID   : 448
 * Publish Date : 2014-02-07 10:45:21
 *
 */

(function($j, undefined){
//I place everything inside a self executing function. It keeps the global
//namespace clean.

  // Configurations are filled by TMS. Javascript will take care of the rest.

  // ------------------  DYNAMICALLY GENERATED -------------------------
	window._sf_startpt=(new Date()).getTime()

	// Chartbeat data
                                           

  var confs = {
    'global_account' : 'UA-18188937-11',
    'station_name' : 'WBUR',
    'station_trackers': ['UA-70853-37'],
    'site_nodes' : [
                        {
        'site_name': 'wbur.org',
        'trackers': [],
        'domain_nodes': [
                                        {
            'domain_name': 'www.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(0|1)[0-9]\/[0-3][0-9]\/.*|\/npr\/\d{9}\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '\/people\/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '\/listen\/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '\/programs\/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Support',
                'regex_pattern': '^\/support\/',
                'pattern_name': 'WBUR support pages'
              },                            {
                'page_type': 'Program',
                'regex_pattern': '\/programs\/.*',
                'pattern_name': 'WBUR Program pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': '\/search\?q\=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'onpoint.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/[0-3][0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '\/about\/people\/.*',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': '\/search\?q\=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'hereandnow.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/[0-3][0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '\/people\/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': 'search.*=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'onlyagame.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/[0-3][0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '/people/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': 'search.*=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'radioboston.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/[0-3][0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '/people/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': 'search.*=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'commonhealth.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '/people/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': 'search.*=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'artery.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/[0-3][0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '/people/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': 'search.*=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'cognoscenti.wbur.org',
            'trackers': [],
                        'website_framework' : '3',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/[0-3][0-9]\/.*',
                'pattern_name': 'WBUR story pages'
              },                            {
                'page_type': 'People',
                'regex_pattern': '/people/',
                'pattern_name': 'WBUR people pages'
              },                            {
                'page_type': 'Streaming',
                'regex_pattern': '/listen/live',
                'pattern_name': 'WBUR Streaming pages'
              },                            {
                'page_type': 'Schedule',
                'regex_pattern': '/programs/schedule',
                'pattern_name': 'WBUR Schedule Pages'
              },                            {
                'page_type': 'Search',
                'regex_pattern': 'search.*=.*',
                'pattern_name': 'WBUR search pages'
              }                                        ]
          },                    {
            'domain_name': 'healthcaresavvy.wbur.org',
            'trackers': [],
                        'website_framework' : '7',
            'patterns': [
                                                        {
                'page_type': 'Story',
                'regex_pattern': '\/20[0-9][0-9]\/(1|0)[0-9]\/.*',
                'pattern_name': 'healthcaresavvy.wbur story page pattern'
              }                                        ]
          }                            ]
      }                ],
    'custom_vars' : {
                          'nid' : {
            'name' : 'nid',
            'slot' : 8,
            'scope_id' : 3          },                  'pop' : {
            'name' : 'pop',
            'slot' : 9,
            'scope_id' : 3          },                  'author' : {
            'name' : 'author',
            'slot' : 11,
            'scope_id' : 3          },                  'keywords' : {
            'name' : 'tags',
            'slot' : 12,
            'scope_id' : 3          },                  'org_id' : {
            'name' : 'org_id',
            'slot' : 13,
            'scope_id' : 3          },                  'brand' : {
            'name' : 'CP_Station',
            'slot' : 14,
            'scope_id' : 2          }            }
  };

  var confs_jquery_events = [
            {
              'trackers': ['UA-18188937-11'],
             'selector' : '#news_toolbar li.audio',
             'category' : 'Engagement',
               'action' : 'Play',
                'label' : 'Flash Player Click Play-Pause',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'div.audio a.pause',
             'category' : 'Engagement',
               'action' : 'Pause',
                'label' : 'streampause',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-listen',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_button_main',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#footer-bottom A',
             'category' : 'Navigation',
               'action' : 'Footer_Bottom',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_ads-right_rail A',
             'category' : 'Navigation',
               'action' : 'Click',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_signup-graphic_signup_link A',
             'category' : 'Navigation',
               'action' : 'Newsletter_block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.read-more',
             'category' : 'Navigation',
               'action' : 'River_Read_more',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.top-header li.events A',
             'category' : 'Navigation',
               'action' : 'Header_Events',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#table-queue-stickystrip A',
             'category' : 'Navigation',
               'action' : 'Sticky_strip',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_footer-pi_footer_top A',
             'category' : 'Navigation',
               'action' : 'Footer_top',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.not-front #related-content-carousel .related-title A',
             'category' : 'Navigation',
               'action' : 'Related_Content_Post_links',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-am',
             'category' : 'Navigation',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_AM',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#announce-small',
             'category' : 'Navigation',
               'action' : 'MHP_announce',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.top-header li.schedule A',
             'category' : 'Navigation',
               'action' : 'Header_Schedule',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-fm',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_FM',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-views-categories-block_politics',
             'category' : 'Navigation',
               'action' : 'MHP_Center_Block_Politics',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-jazz',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_Jazz',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.top-header li.programs A',
             'category' : 'Navigation',
               'action' : 'Header_Programs',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_guide-guide-now-playing-xml A',
             'category' : 'Engagement',
               'action' : 'RR_Listen_block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_rss-feeds A',
             'category' : 'Navigation',
               'action' : 'RR_RSS',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'A.listen_live_link',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'button.playbutton__play.scbutton',
             'category' : 'Engagement',
               'action' : 'Play',
                'label' : 'Streaming_SC_button',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.info-1',
             'category' : 'Navigation',
               'action' : 'Newsletter_block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .now-playing-station',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Now_playing_accordion',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml a.m3u',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Streaming_Now_playing_mp3',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .pl-now .program-name',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Program_name',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml a.windows',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Streaming_Windows_url',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .program-host a',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Program_host',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .amazon',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Purchase_link_amazon',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml div.pl-next',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Up_next',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml a.guide-widget-view-schedule',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Schedule',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml a.itunes',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Streaming_iTunes',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .itunes',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Purchase_link_itunes',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .pl-next-item .program-host a',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Up_next_host',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-xml .pl-next-item .program-name a',
             'category' : 'Engagement',
               'action' : 'Now_playing_Block',
                'label' : 'Up_next_program',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#usual1.usual.ul.li A',
             'category' : 'Engagement',
               'action' : 'Sticky_strip',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#usual1.usual ul.idTabs li a',
             'category' : 'Engagement',
               'action' : 'Tabs_Navigation',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#share.sFacebook',
             'category' : 'Engagement',
               'action' : 'Sharing_button',
                'label' : 'Facebook_Share',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#iconon',
             'category' : 'Engagement',
               'action' : 'Sharing_button',
                'label' : 'Open_sharing',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#share.sTwitter',
             'category' : 'Engagement',
               'action' : 'Sharing_button',
                'label' : 'Twitter_share',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#share.sGoogle',
             'category' : 'Engagement',
               'action' : 'Sharing_button',
                'label' : 'Google_share',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#share.sLinked',
             'category' : 'Engagement',
               'action' : 'Sharing_button',
                'label' : 'LinkedIn_share',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#station',
             'category' : 'Navigation',
               'action' : 'Header_Logo',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.not-front #related-content-carousel .related-title A',
             'category' : 'Navigation',
               'action' : 'Related_Content_Post_Image',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_footer-pi_footer_top A',
             'category' : 'Navigation',
               'action' : 'Footer_top',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#footer-bottom A',
             'category' : 'Navigation',
               'action' : 'Footer_Bottom',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.top-header li.about A',
             'category' : 'Navigation',
               'action' : 'Header_About',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.footer-content a',
             'category' : 'Navigation',
               'action' : 'Footer_Content',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#lead-stories A.ls-image',
             'category' : 'Navigation',
               'action' : 'LeadStory_Image',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-views-local_news-block_local_images',
             'category' : 'Navigation',
               'action' : 'MHP_Local_News_Block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_mainmenu-pi_mainmenu A',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-views-npr_news-block_npr_text',
             'category' : 'Navigation',
               'action' : 'MHP_Center_Block_NPR_Latest',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#header-lockup A',
             'category' : 'Navigation',
               'action' : 'Logo_Header',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.field-name-field-tags A',
             'category' : 'Navigation',
               'action' : 'Post_tags',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#lead-stories H2 A',
             'category' : 'Navigation',
               'action' : 'LeadStory_Link',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_rss_blocks-custom_feed',
             'category' : 'Navigation',
               'action' : 'MHP_RSS_Custom_Feed',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.support',
             'category' : 'Navigation',
               'action' : 'Support_header_btn',
                'label' : 'Support Click',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#table-queue-fleximenu A',
             'category' : 'Navigation',
               'action' : 'Flexi_Menu',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-views-npr_news-block_npr_images',
             'category' : 'Navigation',
               'action' : 'MHP_Center_Block_NPR_Latest',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_quickstats-most_active A',
             'category' : 'Navigation',
               'action' : 'Most_Active_block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.top-header li.now-playing A',
             'category' : 'Navigation',
               'action' : 'Header_NowPlaying',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_pbs_guide-pbs-guide-now-playing',
             'category' : 'Navigation',
               'action' : 'MHP_TV_Radio_block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#pi_featured_featured A',
             'category' : 'Navigation',
               'action' : 'Feat_cont_Rotate4',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.card-text .field-name-field-related-posts A',
             'category' : 'Navigation',
               'action' : 'Related_Content_River_links',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#program_promo-block',
             'category' : 'Navigation',
               'action' : 'MHP_Program_Promo',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#table-queue-promoheader A',
             'category' : 'Navigation',
               'action' : 'SkyBox',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.not-front #related-content-carousel .related-image A',
             'category' : 'Navigation',
               'action' : 'Related_Content_Post_Image',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.top-header li.contact A',
             'category' : 'Navigation',
               'action' : 'Header_Contact',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.car-support',
             'category' : 'Navigation',
               'action' : 'RR_Donate_block',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-am',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_AM',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-WHQR',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_FM',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-WHQR2',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_HD2',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.rss-rss A',
             'category' : 'Engagement',
               'action' : 'RSS_Subscribe',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-music',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_Music',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'UL.playlist LI A',
             'category' : 'Engagement',
               'action' : 'Play',
                'label' : 'In line audio',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.rss-other A',
             'category' : 'Engagement',
               'action' : 'Other_subscribe',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.rss-itunes A',
             'category' : 'Engagement',
               'action' : 'Itunes_subscribe',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-classical',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_Classical',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-news',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_News',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.lightbox.cboxElement',
             'category' : 'Engagement',
               'action' : 'Enlarge_Image',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-2',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_HD2',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-wqcs1',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_button_main',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-wqcs2',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_HD2',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_social-links A',
             'category' : 'Engagement',
               'action' : 'RR_Social_Links',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'span.tagline',
             'category' : 'Engagement',
               'action' : 'Setlist_Powered_by',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#jp_container_1 .push-button',
             'category' : 'Engagement',
               'action' : 'Play',
                'label' : 'Setlist_Play',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.icon-information',
             'category' : 'Engagement',
               'action' : 'Setlist_Info_button',
                'label' : 'InforButtonClick',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.support-wrapper',
             'category' : 'Engagement',
               'action' : 'Setlist_support',
                'label' : 'Setlist_Support',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-events #recent-songs-button',
             'category' : 'Engagement',
               'action' : 'Setlist_Recent_songs',
                'label' : 'Recent-songs',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#menu-btn',
             'category' : 'Engagement',
               'action' : 'Setlist_Menu',
                'label' : 'MenuClick',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#playlist-events #events-button',
             'category' : 'Engagement',
               'action' : 'Setlist_Music_events',
                'label' : 'ShowEvents',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'a.btn-listen2',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_HD2',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#donate A',
             'category' : 'Navigation',
               'action' : 'Support_header_btn',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.stories .story',
             'category' : 'Engagement',
               'action' : 'Player_OnDemand',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-pi_ads-banner_top A',
             'category' : 'Navigation',
               'action' : 'Support Banner',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.inline-audio .jp-play',
             'category' : 'Engagement',
               'action' : 'In line audio-play',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.inline-audio .jp-pause',
             'category' : 'Engagement',
               'action' : 'In line audio-pause',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.social .icon-facebook',
             'category' : 'Engagement',
               'action' : 'Sharing_button_player',
                'label' : 'Player_Facebook_share',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'icon.icon-play',
             'category' : 'Engagement',
               'action' : 'Play',
                'label' : 'Player_Play',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.social .icon-twitter',
             'category' : 'Engagement',
               'action' : 'Sharing_button_player',
                'label' : 'Player_Twitter',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#lead-stories.lead-stories-single',
             'category' : 'Navigation',
               'action' : 'LeadStory_Link',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#block-views-categories-block_more_from_394',
             'category' : 'Navigation',
               'action' : 'More_from_station',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'div.audio-container a.jp-play',
             'category' : 'Mobile:Engagement',
               'action' : 'In line audio-play',
                'label' : 'streaming_mobile_inline',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#jp-play',
             'category' : 'Mobile:Engagement',
               'action' : 'pressed-play-main-audio',
                'label' : 'streaming_mobile_main',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.station-streams .stream-play',
             'category' : 'Mobile:Engagement',
               'action' : 'pressed-play-substream-audio',
                'label' : 'streaming_mobile_substream',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'div.card-twitter a',
             'category' : 'Mobile:Engagement',
               'action' : 'Sharing_button',
                'label' : 'mobile_Twitter_share',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'div.card-facebook a',
             'category' : 'Mobile:Engagement',
               'action' : 'Sharing_button',
                'label' : 'mobile_Facebook_Share',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'div.card-email a',
             'category' : 'Mobile:Engagement',
               'action' : 'Sharing_button',
                'label' : 'mobile_Email_Share',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.still-listening-close',
             'category' : 'Engagement',
               'action' : 'Player_Confirm',
                'label' : 'Confirm Listen',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : 'li.read-story a.link-text',
             'category' : 'Navigation',
               'action' : 'Player_ReadMore',
                'label' : '',
       'use_href_label' : true,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#compareto-select',
             'category' : 'Engagement',
               'action' : 'SAS_Dashboard_Dropdown',
                'label' : 'Select_Compare',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#profile-select',
             'category' : 'Engagement',
               'action' : 'SAS_Dashboard_Dropdown',
                'label' : 'Select_Profile',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#stream-select',
             'category' : 'Engagement',
               'action' : 'SAS_Dashboard_Dropdown',
                'label' : 'Select_Stream',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#segment-select',
             'category' : 'Engagement',
               'action' : 'SAS_Dashboard_Dropdown',
                'label' : 'Select_Segment',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#timespan-select',
             'category' : 'Navigation',
               'action' : 'SAS_Dashboard_Dropdown',
                'label' : 'Select_Time',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#slme_submit',
             'category' : 'Engagement',
               'action' : 'SAS_SLMe_Form',
                'label' : 'Submit_Choices',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.btn.cancel.close-reveal-modal',
             'category' : 'Engagement',
               'action' : 'SAS_SLMe_Form',
                'label' : 'Cancel_SLMe',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#vpr-target',
             'category' : 'Engagement',
               'action' : 'Click',
                'label' : 'VPR Analytics Test',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#on-air-items',
             'category' : 'Engagement',
               'action' : 'Listen_header_btn',
                'label' : 'Streaming_button_Flyout',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#studio_one_header',
             'category' : 'Engagement',
               'action' : 'Stop/Play',
                'label' : 'IowaPlayerStudioOne_stop&play',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#news_header',
             'category' : 'Engagement',
               'action' : 'Stop/Play',
                'label' : 'IowaPlayerNews_stop&play',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#classical_header',
             'category' : 'Engagement',
               'action' : 'Stop/Play',
                'label' : 'IowaPlayerClassical_stop&play',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.sharing-tools li.facebook',
             'category' : 'Navigation',
               'action' : 'Sharing_button',
                'label' : 'SCPR_FacebookShare',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.sharing-tools li.twitter',
             'category' : 'Navigation',
               'action' : 'Sharing_button',
                'label' : 'SCPR_TwitterShare',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.sharing-tools li.gplus',
             'category' : 'Navigation',
               'action' : 'Sharing_button',
                'label' : 'SCPR_GooglePlusShare',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.sharing-tools li.email',
             'category' : 'Navigation',
               'action' : 'Sharing_button',
                'label' : 'SCPR_EmailShare',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.sharing-tools li.print',
             'category' : 'Navigation',
               'action' : 'Print',
                'label' : 'SCPR_Print',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.modal-container h6 a',
             'category' : 'Navigation',
               'action' : 'Now_playing_Block',
                'label' : 'SCPR_EpisodeCurrent',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.modal-container h5 a',
             'category' : 'Navigation',
               'action' : 'Now_playing_Block',
                'label' : 'SCPR_EpisodeSegment',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#support-hero hgroup:last-child a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuOneTimePledge',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.contribute-button-container a',
             'category' : 'Navigation',
               'action' : 'Support_header_btn',
                'label' : 'SCPR_HeaderSupport',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#footer-nav .contribute a',
             'category' : 'Mobile:Navigation',
               'action' : 'Mobile_Support',
                'label' : 'SCPR_MobileSupport',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#most-popular a',
             'category' : 'Navigation',
               'action' : 'Most_Active_block',
                'label' : 'SCPR_MostViewedBlock',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.program a.take-two',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuTakeTwo',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.program a.airtalk',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuAirTalk',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.program a.offramp',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuOffRamp',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#news-mega nav li a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuCategoryNews',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#news-mega .content-types li:first-child a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuAudioNews',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#support-hero hgroup:first-child a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuSustainer',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#footer-support-button a',
             'category' : 'Navigation',
               'action' : 'Support_Footer',
                'label' : 'SCPR_FooterSupport',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.carousel-item a',
             'category' : 'Navigation',
               'action' : 'Click',
                'label' : 'SCPR_InCaseYouMissedIt',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.join_conversation a',
             'category' : 'Navigation',
               'action' : 'Click',
                'label' : 'SCPR_JoinCoversation',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.more-news blockquote a',
             'category' : 'Navigation',
               'action' : 'Click',
                'label' : 'SCPR_CommentSection',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#arts-mega nav li a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuCategoryArts',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#arts-mega .content-types li:first-child a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuArtAudioNews',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.featured h4 a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuNewsStoryContent',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.section .cbase h4 a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'SCPR_MenuBlogPostContent',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.fb-callout a',
             'category' : 'Navigation',
               'action' : 'Click',
                'label' : 'SCPR_FacebookCallout',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.laup a',
             'category' : 'Navigation',
               'action' : 'Click',
                'label' : 'SCPR_LAUP Responsive Banner',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav1 > a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'WAMU Home button',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav2 > a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'WAMU News button',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav9.a',
             'category' : 'Navigation',
               'action' : 'Main_Menu',
                'label' : 'WAMU Donate button',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav3 a.dropdown-link[href="/listen/"]',
             'category' : 'Navigation',
               'action' : 'Menu_Program',
                'label' : 'WAMU Ways to Listen',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://www.npr.org/rss/podcast/podcast_detail.php?siteId=5495237"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU DRS Podcast',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://www.npr.org/rss/podcast/podcast_detail.php?siteId=4985905"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU DRS FNR Podcast',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://www.npr.org/rss/podcast/podcast_detail.php?siteId=9911221"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU KNS Podcast',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://www.npr.org/rss/podcast/podcast_detail.php?siteId=4985900"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU KNS TT Podcast',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://www.npr.org/rss/podcast/podcast_detail.php?siteId=9911225"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU KNS PH Podcast',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://www.npr.org/rss/podcast/podcast_detail.php?siteId=5593992"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU MC Podcast',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.podtitle h3 a[href="http://feeds.wamu.org/WAMU885LocalNewsPodcast"]',
             'category' : 'Navigation',
               'action' : 'Menu_Podcast',
                'label' : 'WAMU Local News',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 .content-section h3 a',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU PIN header',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 .dropdown-tray a.menubutton',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU PIN button',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 .dropdown_header h4 a',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Community header',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="/events"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Events Calendar',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="/events/ticket_giveaways"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Tickets',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="/support/11/07/29/volunteering.php"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Volunteer',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="/contact"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Contact',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="/about/jobs"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Jobs',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="/community"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU More',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="https://www.facebook.com/wamu885"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Facebook',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="http://www.youtube.com/user/wamu885"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU YouTube',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="https://twitter.com/wamu885"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Twitter',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav6 a.dropdown-link[href="http://www.flickr.com/photos/wamu885/"]',
             'category' : 'Navigation',
               'action' : 'Menu_Community',
                'label' : 'WAMU Flickr',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .dropdown_header h4 a[href="/support"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Support',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .dropdown_header h4 a[href="/support/11/07/29/volunteering.php"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Volunteer header',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section.dropdown_left a.dropdown-link[href="/support/12/01/05/wamu_ambassador_program"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Ambassadors',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section.dropdown_left a.dropdown-link[href="/support/12/01/04/daytime_station_support_volunteer_program"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Daytime',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section.dropdown_left a.dropdown-link[href="/support/volunteer/campaign"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Campaign',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section.dropdown_left a.dropdown-link[href="/summerofservice"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Summer',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/affiliates"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Amazon',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/membership/car_donation"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Car',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/11/07/29/workplace_giving.php"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Workplace',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/12/04/20/wamu_young_professionals"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU YIP',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/11/07/29/join_the_leadership_circle.php"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Leadership',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/membership/day_sponsorship"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Day Sponsorship',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support/11/07/29/membership_faq.php"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU FAQ',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section-program-list-item a.dropdown-link[href="/support"]',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU More',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .content-section h3 a',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Donate header',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#topnav8 .dropdown-tray a.menubutton',
             'category' : 'Navigation',
               'action' : 'Menu_Support',
                'label' : 'WAMU Donate button',
       'use_href_label' : false,
      'non_interactive' : false    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.listen-live-player .jp-play',
             'category' : 'Engagement',
               'action' : 'Listen_Live_player',
                'label' : 'Streaming-live',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '#streamcontainer .jp-play',
             'category' : 'Engagement',
               'action' : 'Listen_Live_player',
                'label' : 'Streaming-live',
       'use_href_label' : false,
      'non_interactive' : true    },        {
              'trackers': ['UA-18188937-11'],
             'selector' : '.player .jp-play',
             'category' : 'Engagement',
               'action' : 'Listen_Live_player',
                'label' : 'Streaming-live',
       'use_href_label' : false,
      'non_interactive' : true    }      ];

  // ------------------ END DYNAMICALLY GENERATED -------------------------


  var globalTrackerName = 'npr';

  var cpTags = {
    trackers : [[globalTrackerName, confs.global_account]]
  };


  cpTags.init = function(){
    window._gaq = window._gaq || [];
    // ecommerce
    window._npr = window._npr || [];

    // US3841 Enhanced Link Attribution
    var pluginUrl = '//www.google-analytics.com/plugins/ga/inpage_linkid.js';
    _gaq.push(['_require', 'inpage_linkid', pluginUrl]);
    
    // This is the global tracker
    _gaq.push([globalTrackerName + '._setAccount', confs.global_account]);

    cpTags.setupAccounts(confs.site_nodes, true);

    cpTags.pushAll(['_setAllowLinker', true]);

    cpTags.setDomainName(confs.site_nodes);

    cpTags.setupCustomVars(confs.site_nodes);

    cpTags.setupPatterns(confs.site_nodes);

    // Send basic pageview
    cpTags.pushAll(['_trackPageview']);

    // Send eCommerce Tracking, if present
    cpTags.setupEcommerce();

    // Include ga.js if it doesn't exist on the page yet
    if(typeof window._gat === 'undefined'){
      (function() {
      var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
      // ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
      ga.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'stats.g.doubleclick.net/dc.js';
      var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();
    }

    // setup jQuery dependent specific code
    cpTags.loadjQuery(function(){
      cpTags.setupJQueryEvents(confs_jquery_events);
      cpTags.setupCrossDomain();
      // setup exit link and document download tracking
      cpTags.trackExitAndDownload();
    });

  };

  /**
    * Registers page patterns
   */
  cpTags.setupPatterns = function(nodes){
    var i, j, pats;
    // Look on all nodes
    for (i=0; i<nodes.length; i++){
      if (
        !((nodes[i].site_name && document.location.href.indexOf(nodes[i].site_name) > -1) ||
        (nodes[i].domain_name && document.location.href.indexOf(nodes[i].domain_name) > -1))
      ) { continue; }
      if (typeof nodes[i].patterns !== 'undefined'){
        pats = nodes[i].patterns;
        for (j=0; j<pats.length; j++) {
          if(new RegExp(pats[j].regex_pattern).test(document.location.href)){
            cpTags.pushAll([ '_setCustomVar', 7, 'PageType', pats[j].page_type, 3]);
            return true;
          }
        }
      }
      // Execute for child domain_nodes as well
      if (typeof nodes[i].domain_nodes !== 'undefined') {
        if (cpTags.setupPatterns(nodes[i].domain_nodes) === true) {
          return true;
        }
      }
    }
  };

  /**
   * Sets all Custom Vars. Currently only StationName
   */
  cpTags.setupCustomVars = function(nodes){
    var station_name = confs.station_name;
    if(station_name){
      cpTags.pushAll(['_setCustomVar', 6, 'Station', station_name, 2]);
    }
    
      };

  function domainMatch(domain, location) {
     match = false;    
  
     location = stripProtocol(location);
     
     // if the domain name contains slashes we return an exact match
     // in order to account for domain names that are not in accordance 
     // with standards.
     if (domain.indexOf("/") > -1 ) {
       if (location == domain) {
         match = true;
       }
     } else {
       location = hostnameFromURLWithoutProtocol(location);
       if(location == domain) {
          match = true;
       }
     }
     return match;
  }
  
  function stripProtocol(url) {
    var withoutProtocol = '';
    var protocolAndRest = url.split('//');
    if (protocolAndRest.length > 1) {
      withoutProtocol = protocolAndRest[1];
    }
    return withoutProtocol;
  }

  function hostnameFromURLWithoutProtocol(urlWithoutProtocol) {
    var hostname = '';
    var segments = urlWithoutProtocol.split('/');
    if (segments.length > 0) {
      hostname = segments[0];
    }
    return hostname;
  }
  
  /**
   * Calls _setAccount and cache trackers on cpTags.trackers
   *
   * TODO: first_call is an ugly hack to get the recursion right. I can do better
   */
  cpTags.setupAccounts = function(nodes, first_call){
    var next,i,j;


    // Setup Station Trackers
    if(first_call) {
      for (i=0; i<confs.station_trackers.length; i++) {
        next = 'station'+cpTags.trackers.length;
        cpTags.trackers.push([next, confs.station_trackers[i]]);
        _gaq.push([next + '._setAccount', confs.station_trackers[i]]);
      }
    }

    for (i=0; i < nodes.length; i++) {
      // Check if this node doesn't apply to the current page
      if (
        !((nodes[i].site_name && document.location.href.indexOf(nodes[i].site_name) > -1) || 
          nodes[i].domain_name && domainMatch(nodes[i].domain_name, document.location.href))
      ) { continue; }

      if (nodes[i].trackers && nodes[i].trackers.length > 0) {
        for(j=0; j< nodes[i].trackers.length; j++){
          // add Trackers
          if(first_call) {
            next = 'site'+cpTags.trackers.length;
          } else {
            next = 'domain'+cpTags.trackers.length;
          }
          cpTags.trackers.push([next, nodes[i].trackers[j]]);
          _gaq.push([next+'._setAccount', nodes[i].trackers[j]]);
        }
      }
      if (nodes[i].domain_nodes){
        // Recursive call for domain_nodes
        cpTags.setupAccounts(nodes[i].domain_nodes, false);
      }
    }
  };

  /**
   * Calls setdomainName trying to use one of the site_nodes
   */
  cpTags.setDomainName = function(site_nodes){
    var i;
    for (i=0; i < site_nodes.length; i++) {
      if (document.location.hostname.indexOf(site_nodes[i].site_name) >= 0){
        return cpTags.pushAll(['_setDomainName', site_nodes[i].site_name]);
      }
    }
  };

  /**
   * Receives a list of accounts, followed by pushed elements.
   * Executes the pushed GA calls for specified trackers
   */
  cpTags.pushExplicit = function(target_accounts){
    try {
      var tracker, a, b, func,
          args = Array.prototype.slice.call(arguments,1),
          target_trackers = [];

      // Finds the tracker where the push is targeted and are also available on the page
      for (a=0; a<target_accounts.length; a++) {
        for (b=0; b<cpTags.trackers.length; b++) {
          if(cpTags.trackers[b][1] == target_accounts[a]){
            target_trackers.push(cpTags.trackers[b]);
          }
        }
      }
      for (a=0; a < args.length; a++) {
        func = args[a].shift();
        for (tracker=0; tracker < target_trackers.length; tracker++) {
          _gaq.push(
            ([target_trackers[tracker][0] + '.' + func]).concat(args[a])
          );
        }
      }
    } catch (e) {cpTags.handleException(e);}
  };

  /**
   * Receives a list of pushed GA calls and execute them for all trackers
   */
  cpTags.pushAll = function(){
    try {
      var tracker, a, func,
          args = Array.prototype.slice.call(arguments),
          target_trackers = cpTags.trackers;

      for (a=0; a < args.length; a++) {
        func = args[a].shift();
        for (tracker=0; tracker < target_trackers.length; tracker++) {
          _gaq.push(
            ([target_trackers[tracker][0] + '.' + func]).concat(args[a])
          );
        }
      }
    } catch (e) {cpTags.handleException(e);}
  };

  cpTags.handleException = function(e){
    //console.log('Exception Raised!', e);
  }

  /**
   * Setup jQuery Events
   */
  cpTags.setupJQueryEvents = function(jevents) {
    try {
      if(jevents === undefined) return;
      for (var i=0; i<jevents.length; i++) {
        (function (je){
          $j(je.selector).live('mousedown', function(){
            var el = $j(this);
            cpTags.pushExplicit(je.trackers, [
              '_trackEvent',
              je.category,
              je.action,
              je.use_href_label ? el.attr('href')  : je.label,
              je.value,
              je.non_interactive
            ]);
          });
        })(jevents[i]);
      }
    } catch (e) {cpTags.handleException(e);}
  };

  /**
   * Make sure jQuery is loaded or load it from Google CDN and execute callback when it's done
   */
  cpTags.loadjQuery = function(cb){
    try {
    
    if (typeof $j !== 'undefined' && parseFloat($j.fn.jquery) == 1.7) {
        return cb();
      }
      /*!
        * $script.js Async loader & dependency manager
        * https://github.com/ded/script.js
        * (c) Dustin Diaz, Jacob Thornton 2011
        * License: MIT
        */
      (function(a,b,c){typeof c["module"]!="undefined"&&c.module.exports?c.module.exports=b():typeof c["define"]!="undefined"&&c["define"]=="function"&&c.define.amd?define(a,b):c[a]=b()})("$script",function(){function p(a,b){for(var c=0,d=a.length;c<d;++c)if(!b(a[c]))return j;return 1}function q(a,b){p(a,function(a){return!b(a)})}function r(a,b,i){function o(a){return a.call?a():d[a]}function t(){if(!--n){d[m]=1,l&&l();for(var a in f)p(a.split("|"),o)&&!q(f[a],o)&&(f[a]=[])}}a=a[k]?a:[a];var j=b&&b.call,l=j?b:i,m=j?a.join(""):b,n=a.length;return setTimeout(function(){q(a,function(a){if(h[a])return m&&(e[m]=1),h[a]==2&&t();h[a]=1,m&&(e[m]=1),s(!c.test(a)&&g?g+a+".js":a,t)})},0),r}function s(c,d){var e=a.createElement("script"),f=j;e.onload=e.onerror=e[o]=function(){if(e[m]&&!/^c|loade/.test(e[m])||f)return;e.onload=e[o]=null,f=1,h[c]=2,d()},e.async=1,e.src=c,b.insertBefore(e,b.firstChild)}var a=document,b=a.getElementsByTagName("head")[0],c=/^https?:\/\//,d={},e={},f={},g,h={},i="string",j=!1,k="push",l="DOMContentLoaded",m="readyState",n="addEventListener",o="onreadystatechange";return!a[m]&&a[n]&&(a[n](l,function t(){a.removeEventListener(l,t,j),a[m]="complete"},j),a[m]="loading"),r.get=s,r.order=function(a,b,c){(function d(e){e=a.shift(),a.length?r(e,d):r(e,b,c)})()},r.path=function(a){g=a},r.ready=function(a,b,c){a=a[k]?a:[a];var e=[];return!q(a,function(a){d[a]||e[k](a)})&&p(a,function(a){return d[a]})?b():!function(a){f[a]=f[a]||[],f[a][k](b),c&&c(e)}(a.join("|")),r},r},this);
      // Load jQuery and executes callback
      jqPath = ('https:' == document.location.protocol ? 'https://' : 'http://')
        + 'ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js';
      this.$script([jqPath], function(){
        $j = window.jQuery.noConflict(true);
        cb();
      });
    } catch (e) {cpTags.handleException(e);}
  };

  /**
   * Tags all crossDomain Links. Depends on jQuery
   */
  cpTags.setupCrossDomain = function setupCrossDomain() {
    
    function respondToClick(event) {
      // Regex to make sure it's the domain we're getting
      var r = new RegExp('^https?://(.+\.)?'+ this.site + '($|/)');
      var linkSel = $j(event.currentTarget);
      var linkHref = linkSel.attr('href');

      if (r.test(linkHref) && !cpTags.shouldExcludeLink(linkSel)) {
        if (linkSel.attr('target') === '_blank') {
          _gaq.push(function(){
            var t = _gat._getTrackers()[0];
            window.open(t._getLinkerUrl(linkHref));
          });
        }       
        else if(linkSel.hasClass('xpopup')) { // US4397
          _gaq.push(function() {
            var t = _gat._getTrackers()[0];
            var linkerUrl = t._getLinkerUrl(linkHref);
          }); 
        }        
        else {
          _gaq.push([globalTrackerName + '._link', linkHref]);
        }
        event.preventDefault();
      }
    }

    try {
      for (var i = 0; i < confs.site_nodes.length; ++i){
        var site = confs.site_nodes[i].site_name;

        // Check to see if it's not the current domain
        if (document.location.hostname === site ||
          document.location.hostname.indexOf('.' + site) > -1) { 
          continue; 
        }

        var eventResponderContext = {site: site};
        
        // us4397
        $j('a[href*="'+site+'"]').each(function(index, element) {
	  if ($j(this).hasClass('xpopup')) { 
            // check for target != '_blank'
            var linkHref = $j(this).attr('href');
            var t = _gat._getTrackers()[0];
            $j(this).attr('href', t._getLinkerUrl(linkHref));
	  }
         });

        // tag all links
        $j('a[href*="'+site+'"]').live('click', 
          respondToClick.bind(eventResponderContext));
      }
    }
    catch (e) {
      cpTags.handleException(e);
    }
  };

  cpTags.shouldExcludeLink = function shouldExcludeLink(linkSel) {
    var shouldExclude = false;
    var classAttrs = linkSel.attr('class');
    if (classAttrs && classAttrs.indexOf('lightbox') !== -1) {
      shouldExclude = true;
    }
    return shouldExclude;
  };

  /**
   * Track downloads for document types
   * txt pdf doc xls xlsx ppt pps odt ods odp ico
   * and exit links
   */
  cpTags.trackExitAndDownload = function() {
    if (typeof $j != 'undefined') {
      $j(document).ready(function($) {
        var filetypes = /\.(txt|pdf|doc|xls|xlsx|ppt|pps|odt|ods|odp|ico)$/i;
        var baseHref = '';
        if ($j('a').attr('href') != undefined) {
          baseHref = $j('a').attr('href');
        }

        // build a list of domains for this site
        domainNames = '';
        for (i = 0; i < confs.site_nodes.length; i++){
          s = confs.site_nodes[i];
          for (j = 0; j < s['domain_nodes'].length; j++) {
            domainNames = domainNames + s['domain_nodes'][j].domain_name + ' ';
          }
       }

        $j('a').each(function() {
          var href = $j(this).attr('href');
          var hrefElements = (href) ? href.split('/') : [];
          var hrefDomain = (hrefElements.length > 2) ? hrefElements[2] : href;

           if (href && (href.match(/^https?\:/i)) && domainNames.indexOf(hrefDomain) < 0) {
            $j(this).click(function() {
              var extLink = href.replace(/^https?\:\/\//i, '');
              cpTags.pushAll(['_trackEvent', 'External', 'Click-Exit Link', extLink]);
              if ($j(this).attr('target') != undefined && $j(this).attr('target').toLowerCase() != '_blank') {
                setTimeout(function() { location.href = href; }, 200);
                return false;
               }
            });
          } else if (href && href.match(filetypes)) {
            $j(this).click(function() {
              var extension = (/[.]/.exec(href)) ? /[^.]+$/.exec(href) : undefined;
              var filePath = href;
              var extensionStr = 'Download-'+ extension;
              cpTags.pushAll(['_trackEvent', 'Download', extensionStr, filePath]);
              if ($j(this).attr('target') != undefined && $j(this).attr('target').toLowerCase() != '_blank') {
                setTimeout(function() { location.href = href; }, 200);
                return false;
              }

            });
          }
        });
      });
    };
  }


  // Grab any eCommerce Tracking meant for distribution to all trackers
  cpTags.setupEcommerce = function(){
    try
    {
      var bux;
      while(bux = _npr.shift())
      {
         if(bux[0]=='_addTrans'||bux[0]=='_addItem'||bux[0]=='_trackTrans')
         {
            cpTags.pushAll(bux);
         }
      }
    } catch (e) {cpTags.handleException(e);}
  };

  // Run it.
  cpTags.init();

  // XXX Debug
  window.cpTags = cpTags;


  // chartbeat code
  if(typeof( _sf_async_config) !== 'undefined') {
	  (function() {
	    function loadChartbeat() {
	      window._sf_endpt = (new Date()).getTime();
	      var e = document.createElement('script');
	      e.setAttribute('language', 'javascript');
	      e.setAttribute('type', 'text/javascript');
	      e.setAttribute('src',
	        (("https:" == document.location.protocol) ? "https://a248.e.akamai.net/chartbeat.download.akamai.com/102508/" : "http://static.chartbeat.com/") +
	        "js/chartbeat.js");
	      document.body.appendChild(e);
	    };
	    var oldonload = window.onload;
	    window.onload = (typeof window.onload != 'function') ?
	      loadChartbeat : function() { oldonload(); loadChartbeat(); };
	   })();
  }

})(window.jQuery);


