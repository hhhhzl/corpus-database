





'use strict';

/* ===== Enable Bootstrap Popover (on element  ====== */

var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})

/* ==== Enable Bootstrap Alert ====== */
var alertList = document.querySelectorAll('.alert')
alertList.forEach(function (alert) {
  new bootstrap.Alert(alert)
});


/* ===== Responsive Sidepanel ====== */
// const sidePanelToggler = document.getElementById('sidepanel-toggler'); 
// const sidePanel = document.getElementById('app-sidepanel');  
// const sidePanelDrop = document.getElementById('sidepanel-drop'); 
// const sidePanelClose = document.getElementById('sidepanel-close'); 

// window.addEventListener('load', function(){
// 	responsiveSidePanel(); 
// });

// window.addEventListener('resize', function(){
// 	responsiveSidePanel(); 
// });


// function responsiveSidePanel() {
//     let w = window.innerWidth;
// 	if(w >= 1200) {
// 	    // if larger 
// 	    //console.log('larger');
// 		sidePanel.classList.remove('sidepanel-hidden');
// 		sidePanel.classList.add('sidepanel-visible');
		
// 	} else {
// 	    // if smaller
// 	    //console.log('smaller');
// 	    sidePanel.classList.remove('sidepanel-visible');
// 		sidePanel.classList.add('sidepanel-hidden');
// 	}
// };

// sidePanelToggler.addEventListener('click', () => {
// 	if (sidePanel.classList.contains('sidepanel-visible')) {
// 		console.log('visible');
// 		sidePanel.classList.remove('sidepanel-visible');
// 		sidePanel.classList.add('sidepanel-hidden');
		
// 	} else {
// 		console.log('hidden');
// 		sidePanel.classList.remove('sidepanel-hidden');
// 		sidePanel.classList.add('sidepanel-visible');
// 	}
// });



// sidePanelClose.addEventListener('click', (e) => {
// 	e.preventDefault();
// 	sidePanelToggler.click();
// });

// sidePanelDrop.addEventListener('click', (e) => {
// 	sidePanelToggler.click();
// });



/* ====== Mobile search ======= */
const searchMobileTrigger = document.querySelector('.search-mobile-trigger');
const searchBox = document.querySelector('.app-search-box');

searchMobileTrigger.addEventListener('click', () => {

	searchBox.classList.toggle('is-visible');
	
	let searchMobileTriggerIcon = document.querySelector('.search-mobile-trigger-icon');
	
	if(searchMobileTriggerIcon.classList.contains('fa-search')) {
		searchMobileTriggerIcon.classList.remove('fa-search');
		searchMobileTriggerIcon.classList.add('fa-times');
	} else {
		searchMobileTriggerIcon.classList.remove('fa-times');
		searchMobileTriggerIcon.classList.add('fa-search');
	}
	
		
	
});




var app=new Vue({
	el: '#app',
	data: {
		list:[
		
		],
	},
	mounted:function(){
		this.flush()
		
	},
	methods:{
		flush:function(){
			var that=this;
			
			axios({
				url: '/find',
				params: {
					"pageNum":1
				}
			}).then(function (response) {
				that.list=[]
					for(var i=0;i<response.data.length;i++){
						that.list.push(response.data[i])
					}		
				})
				.catch(function (error) {
					console.log(error);
				});
		}
	}
})

var nav=new Vue({
		el: '#nav',
		data: {
			cur:1
		},
		// 在 `methods` 对象中定义方法
		methods: {
			nav: function (tar) {
				nav.cur=tar;
				paging.flush()
				
			},
			
		}
	})


var graph=new Vue({
	el: '#graph',
	data: {
		hidden:true
	},
	// 在 `methods` 对象中定义方法
	methods: {
		open:function(){

			this.hidden=false

		},
		close_card:function () {
			this.hidden=true
		}
		
		
	}
})



new Vue({
		el: '#button',
		data: {
			name: 'Vue.js'
		},
		// 在 `methods` 对象中定义方法
		methods: {
			upload: function (event) {
				this.$refs['fileInput'].click()
			},
			onFilesChanged: function (event) {
				event.preventDefault();
				let formData = new FormData()
				let file = this.$refs.fileInput.files[0]
				formData.append('file',file)
				axios({
					url: '/upload',
					method: 'post',
					data: formData,
					headers: {
						'Content-Type': 'multipart/form-data'
					}
				}).then((res) => {
						alert("上传成功")
					paging.flush()
					paging.count()
				}).catch((e) => {
						})
			}
		}
	})


var paging=new Vue({
		el: '#paging',
		data: {
			name: 'Vue.js',
			cur:1,
			all:100
		},
		// 在 `methods` 对象中定义方法
		mounted(){
			this.count()
		},
		methods: {
			count:function(){
				axios
				.get('/count')
				.then(response => (
					this.all=response.data
				))
				.catch(function (error) { // 请求失败处理
					console.log(error);
				});
			},
			flush:function(){
				this.cur=1
				var that=this
				axios({
					url: '/find',
					params: {
						"pageNum":this.cur,
						'partOfSpeech':nav.cur
					}
				}).then(function (response) {
						app.list=[]
						for(var i=0;i<response.data.length;i++){
							app.list.push(response.data[i])
						}		
					})
					.catch(function (error) {
						console.log(error);
					});
			},
			next:function(){
				var that=this
				axios({
					url: '/find',
					params: {
						"pageNum":this.cur+1,
						'partOfSpeech':nav.cur
					}
				}).then(function (response) {
						app.list=[]
						for(var i=0;i<response.data.length;i++){
							app.list.push(response.data[i])
						}		
						that.cur+=1		
					})
					.catch(function (error) {
						console.log(error);
					});
			},
			prev:function(){
				var that=this
				axios({
					url: '/find',
					params: {
						"pageNum":this.cur-1,
						'partOfSpeech':nav.cur
					}
				}).then(function (response) {
						app.list=[]
						for(var i=0;i<response.data.length;i++){
							app.list.push(response.data[i])
						}		
						that.cur-=1
					})
					.catch(function (error) {
						console.log(error);
					});
			}
		}
	})

var myChart = echarts.init(document.getElementById('main'));
 // 指定图表的配置项和数据
 var option = {
title: {
	text: '知识关系图'
},
tooltip: {},
animationDurationUpdate: 1500,
animationEasingUpdate: 'quinticInOut',
series: [
	{
	type: 'graph',
	layout: 'none',
	symbolSize: 50,
	roam: true,
	label: {
		show: true
	},
	edgeSymbol: ['circle', 'arrow'],
	edgeSymbolSize: [4, 10],
	itemStyle:{
		color:"#5470C6"
	},
	data: [
		{
		name: '流固耦合',
		x: 300,
		y: 300
		},
		{
		name: '固体',
		x: 550,
		y: 100
		},
		{
		name: '物理',
		x: 550,
		y: 500
		}
	],
	// links: [],
	links: [
		{
		source: 0,
		target: 2,
		label: {
			show: true,
			formatter:"所属学科"
		},
		lineStyle: {
			curveness: 0.2
		}
		},
		{
		source: 0,
		target: 1,
		label: {
			show: true,
			formatter:"交叉学科"
		},
		lineStyle: {
			curveness: 0.2
		}
		}
		
	],
	lineStyle: {
		opacity: 0.9,
		width: 2,
		curveness: 0
	}
	}
]
};

// 使用刚指定的配置项和数据显示图表。
myChart.setOption(option);

