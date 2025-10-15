setTimeout(function() {
  if (window.innerWidth < 1199.99) {
    $('.mobile-app-box').parents('body').addClass('social-body');
  }
  function isMobile() {
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }
  if (isMobile()) {
      if (/android/i.test(navigator.userAgent)) {
        $('.mobile-app-link').attr("href", "https://play.google.com/store/apps/details?id=com.internationalcapitalmarketsptyltd.pelican");
      }

      if (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream) {
        $('.mobile-app-link').attr("href", "https://apps.apple.com/gb/app/ic-social/id1619346047");
      }
  }
}, 100);

$('.app-bar-close').click(() => {
  $('.mobile-app-box').hide();
  $('body').removeClass('social-body');
});

$('.menubar').click(() => {
  $('.menubar').toggleClass('open');
  $('.header-nav').toggleClass('open');
  $('html').toggleClass('overflow-hidden');
});

$('.expand-arrow').click((e) => {
  $(e.currentTarget).toggleClass('active');
  $(e.currentTarget).siblings('.dropdown-menu').addClass('open').slideToggle();
});

$('.mbl-pagi-toggle').click(() => {
  $('.mbl-pagi-toggle').toggleClass('open');
  $('.pag-toggle').toggleClass('open');
  $('.pagtab-list').slideToggle();
});

$('.skin-toggle').click((e) => {
  var $button = $(e.currentTarget);
  var $panel = $button.closest('.markets-spread-table');
  var $table = $panel.find('.single-design-table');
  var switchSkinTo = ($button.is('.skin-light') ? 'light-skin' : 'dark-skin');
  $table.toggleClass('light-skin', false).toggleClass('dark-skin', false).toggleClass(switchSkinTo, true);
});

$(".scroll").click(function(e) {
  e.preventDefault();
  var aid = $(this).attr("href");
  $('html,body').animate({scrollTop: $(aid).offset().top},'slow');
});

$('input.spreads-search-box').on('input', function (e) {
  var $input = $(e.currentTarget);
  var value = $input.val();
  var $panel = $(e.currentTarget).closest('.markets-spread-table');
  $panel.find(".symbol-group-toggle").toggleClass('symbol-group-active', false);
  var $table = $panel.find('.single-design-table');
  var $row = $table.find('.table-row');
  $row.show();
  if (value && value.length) {
      $row.each(function () {
          var $currentRow = $(this);
          var $nameCell = $currentRow.find('.table-cell.c1');
          var name = $nameCell.text();
          if (name && name.toUpperCase().indexOf(value.toUpperCase()) === -1) {
              $currentRow.hide();
          }
      });
  }
});


$('.popup-modal.tf').on('click', function () {
  $('.popup-modal.tf').hide();
});
$('#tf').on('click', function () {
  $('.popup-modal.tf').show();
});

$('.symbol-group-toggle').click((e) => {
    $(".symbol-group-toggle").removeClass('symbol-group-active');
    var $selectedGroupTab = $(e.currentTarget);
    $selectedGroupTab.addClass('symbol-group-active');
    var selectedGroup = $selectedGroupTab.text();
    var $panel = $(e.currentTarget).closest('.markets-spread-table');
    var $table = $panel.find('.single-design-table');
    var $row = $table.find('.table-row');
    $row.show();
    if (selectedGroup) {
        $row.each(function () {
            var $currentRow = $(this);
            var $symbolGroupCell = $currentRow.find('.table-cell.c-symbol-group');
            var symbolGroup = $symbolGroupCell.text();
            if (symbolGroup !== selectedGroup) {
                $currentRow.hide();
            }
        });
    }
});

$('.table-div-hov').hover((e) => {
  $(e.currentTarget).siblings('.table-div-hov').removeClass('hover');
  $(e.currentTarget).addClass('hover');
});

$('.pkg-card').hover((e) => {
  $(e.currentTarget).parents('.content-sec').find('.pkg-card').removeClass('hover');
  $(e.currentTarget).addClass('hover');
});

$(".table-div-detail ul li").hover(
  function(e) {
    $('.table-div-detail ul li').removeClass('hover');
    var index = $(e.currentTarget).index();
    $(e.currentTarget).parents('.table-div').find('.table-div-single').each((single, ind) => {
      $(ind).find('li').eq(index).addClass('hover');
    })
  }, function() {
    $('.table-div-detail ul li').removeClass('hover');
  }
);

function scrollHeader() {
  var scroll = $('html').scrollTop();
  var val;
  if (scroll >= 100) {
    $(".icm-navbar.affix-top").addClass("fixed");
    if ($(window).width() > 767) {
      // val = $('.icm-navbar.affix-top').height() - $('.header').height()
      // $(".icm-navbar.affix-top").css("transform", `translateY(-${val}px)`);
    }
    else {
      // val = $('.icm-navbar.affix-top').height() - $('.header').height() - $('.topbar').height() - 16
      // $(".icm-navbar.affix-top").css("transform", `translateY(-${val}px)`);
    }
  } else {
    $(".icm-navbar.affix-top").removeClass("fixed");
    //$(".icm-navbar.affix-top").css("transform", `translateY(0px)`);
  }
}
scrollHeader()


var lastScrollTop = 0;
$(window).scroll(function() {
  scrollHeader()

  var scrollTop = $(this).scrollTop();
  if (scrollTop > lastScrollTop) {
    // User is scrolling down
    $('.fixed-bottom-strip').removeClass('scrolled-up');
  } else {
    // User is scrolling up
    $('.fixed-bottom-strip').addClass('scrolled-up');
  }
  lastScrollTop = scrollTop;
});

if($('#homepagecarousel').length > 0) {
  function assigndataBsSlideTo() {
    var dataBsSlideTo = $('.carousel-indicators button');
    
    for (var i = 0; i < dataBsSlideTo.length; i++) {
      $(dataBsSlideTo[i]).attr('data-bs-slide-to', i);
    }
  }
  assigndataBsSlideTo()
}