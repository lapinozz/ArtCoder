class App
{
	constructor()
	{
		this.events = {};

		this.oldSettings = {};
		this.settings = JSON.parse(localStorage.getItem('settings')) || {};

		this.oldProps = {};
		this.props = {
			styles: [],
			contents: []
		};

		for(const prop in this.props)
		{			
			this.on(prop, this.setProp.bind(this, prop));
		}

		const appDiv = makeDiv('div', {
			parent: document.body,
			class: 'app',
		});

		const sectionsDiv = makeDiv('div', {
			parent: appDiv,
			class: 'sections',
		});

		const sectionIds = ['data', 'contents', 'basic', 'styles', 'styled'];
		const sections = {};

		for(const sectionId of sectionIds)
		{
			const section = {};

			sections[sectionId] = section;

			section.rootDiv = makeDiv('div', {
				parent: sectionsDiv,
				class: ['section', sectionId],
			});

			section.titleDiv = makeDiv('div', {
				parent: section.rootDiv,
				class: 'title',
				innerText: capitalizeFirstLetter(sectionId)
			});

			section.errorDiv = makeDiv('div', {
				parent: section.rootDiv,
				class: 'error',
			});

			section.contentDiv = makeDiv('div', {
				parent: section.rootDiv,
				class: 'content',
			});

			section.onError = (error) => 
			{
				clearTimeout(section.errorTimeout);
				section.errorTimeout = setTimeout(() =>
				{
					section.errorDiv.innerText = '';
				}, 5000);

				section.errorDiv.innerText = error.message;
			};

			const func = this['setup' + capitalizeFirstLetter(sectionId)];
			func && func.call(this, section);
		}

		this.on('error', (error) => 
		{
			console.error(error);
			sections[error.state].onError(error);
		});

		const sidebarContainer = this.setupSidebar(appDiv);

		this.setupSettings(sidebarContainer);
		this.setupProfiles(sidebarContainer);

		this.trigger('settingsUpdate');
	}

	onConnectionOpen()
	{
		for(const id in this.settings)
		{			
			this.setSetting(id, this.settings[id]);
		}
	}

	on(event, callback)
	{
		const events = this.events[event] || (this.events[event] = []);
		events.push(callback); 
	}

	trigger(event)
	{
		const events = this.events[event];

		if(!events)
		{
			return;
		}

		const args = Array.prototype.slice.call(arguments, 1);

		for(const callback of events)
		{
			callback(...args);
		}
	}

	setProp(id, value)
	{
		this.oldProps[id] = this.props[id];
		this.props[id] = value;
		this.triggerPropUpdate(id);
	}

	triggerPropUpdate(id)
	{
		const funcName = 'update' + capitalizeFirstLetter(id);
		const func = this[funcName];

		if(func)
		{
			func.call(this, this.props[id], this.oldProps[id]);
		}
	}

	setSetting(id, value)
	{
		this.oldSettings[id] = this.settings[id];
		this.settings[id] = value;

		const data = {};
		data[id] = value;

		sendMessage(id, data);

		localStorage.setItem('settings', JSON.stringify(this.settings));

		this.trigger(id, value);
	}

	getSetting(id, value)
	{
		return this.settings[id];
	}

	makeOptions(optionsDiv, options)
	{
		for(const option of options)
		{
			const optionDiv = makeDiv('div', {
				parent: optionsDiv,
				class: 'option',
			});

			const labelDiv = makeDiv('label', {
				parent: optionDiv,
				class: 'label',
				for: option.id,
				innerText: option.label
			});

			if(option.type == 'number')
			{
				const numberDiv = makeDiv('div', {
					parent: optionDiv,
					class: 'number-input',
				});

				const inputDiv = makeDiv('input', {
					parent: numberDiv,
					...option,
					class: 'input',
					onchange: () => this.setSetting(option.id, inputDiv.value),
				});

				const buttonUpDiv = makeDiv('div', {
					parent: numberDiv,
					type: 'button',
					class: 'button button-up',
					innerText: '+',
					onclick: () => {inputDiv.stepUp(); inputDiv.onchange();}
				});

				const buttonDownDiv = makeDiv('div', {
					parent: numberDiv,
					type: 'button',
					class: 'button button-down',
					innerText: '-',
					onclick: () => {inputDiv.stepDown(); inputDiv.onchange();}
				});

				this.on('settingsUpdate', () =>
				{
					inputDiv.value = this.getSetting(option.id) || option.default;
					inputDiv.onchange();
				});
			}
			else if(option.type == 'play')
			{
				const inputDiv = makeDiv('input', {
					parent: optionDiv,
					type: 'button',
					class: 'play'
				});

				let value;

				const update = () =>
				{
					inputDiv.value = value ? '\uf04c' : '\uf04b';
					this.setSetting(option.id, value);
				};

				this.on('settingsUpdate', () =>
				{
					value = this.getSetting(option.id);
					if(value === undefined)
					{
						value = option.default;
					}

					update();
				});

				inputDiv.onclick = () => 
				{
					value = !value;
					update();
				};
			}
		}
	}

	setupSidebar(appDiv)
	{
		const sidebarRoot = makeDiv('div', {
			parent: appDiv,
			class: 'sidebar-root',
		});

		const sidebarContainer = makeDiv('div', {
			parent: sidebarRoot,
			class: 'container',
		});

		const toggleDiv = makeDiv('div', {
			parent: sidebarContainer,
			class: 'toggle',
			onclick: () => 
			{
				sidebarRoot.classList.toggle('open');
			}
		});

		sidebarRoot.classList.add('open');

		return sidebarContainer;
	}

	setupSettings(sidebarContainer)
	{
		const sectionDiv = makeDiv('div', {
			parent: sidebarContainer,
			class: 'section',
		});

		const titleDiv = makeDiv('div', {
			parent: sectionDiv,
			class: 'title',
			innerText: 'Settings'
		});

		const settingsDiv = makeDiv('div', {
			parent: sectionDiv,
			class: 'settings',
		});

	}

	setupProfiles(sidebarContainer)
	{
		const sectionDiv = makeDiv('div', {
			parent: sidebarContainer,
			class: 'section',
		});

		const titleDiv = makeDiv('div', {
			parent: sectionDiv,
			class: 'title',
			innerText: 'Profiles'
		});

		const addDiv = makeDiv('div', {
			parent: titleDiv,
			class: 'add',
		});

		const profilesDiv = makeDiv('div', {
			parent: sectionDiv,
			class: 'profiles',
		});

		const profiles = {};

		const makeName = (name) =>
		{
			let tryName = name;
			let index = 2;
			while(true)
			{
				if(!profiles[tryName])
				{
					return tryName;
				}

				tryName = name + index++;
			}
		};

		const saveProfiles = () =>
		{
			localStorage.setItem('profiles', JSON.stringify(profiles));
		}

		const addProfile = (id, values) =>
		{
			const profileDiv = makeDiv('div', {
				parent: profilesDiv,
				class: 'profile',
			});

			const profile = {
				...values,
				id: makeName(id)
			};

			profiles[profile.id] = profile;

			profile.nameDiv = makeDiv('input', {
				parent: profileDiv,
				class: 'name',
				value: profile.id,
				oninput: () => 
				{
					delete profiles[profile.id];
					profile.id = makeName(profile.nameDiv.value);
					profiles[profile.id] = profile;
					saveProfiles();
				},
				onkeydown: (event) =>
				{
					if(event.keyCode==13)
					{ 
						profile.nameDiv.blur();
						return false;
					}
				}
			});

			profile.saveDiv = makeDiv('input', {
				parent: profileDiv,
				type: 'button',
				class: 'save',
				value: 'update',
				onclick: () => 
				{
					profile.settings = JSON.parse(JSON.stringify(this.settings));
					saveProfiles();
				}
			});

			profile.loadDiv = makeDiv('input', {
				parent: profileDiv,
				type: 'button',
				class: 'load',
				value: 'load',
				onclick: () =>
				{
					this.settings = JSON.parse(JSON.stringify(profile.settings));
					this.trigger('settingsUpdate');
				}
			});

			profile.deleteDiv = makeDiv('div', {
				parent: profileDiv,
				class: 'delete',
				innerText: '\uf1f8',
				title: 'Delete Profile',
				onclick: () => 
				{
					delete profiles[profile.id];
					profileDiv.remove();
					saveProfiles();
				}
			});

			return profile;
		};

		addDiv.onclick = () => 
		{
			const profile = addProfile('profile');
			profile.saveDiv.onclick();
		};

		const loadedProfiles = JSON.parse(localStorage.getItem('profiles') || '{}');
		for(const id in loadedProfiles)
		{
			addProfile(id, loadedProfiles[id]);
		}
	}

	setupData(section)
	{
		let handle = null;

		const textarea = makeDiv('textarea', {
			parent: section.contentDiv,
			class: 'text',
			oninput: () => 
			{
				clearTimeout(handle);
				handle = setTimeout(() => textarea.onchange(), 1000);
			},
			onchange: () => 
			{					
				if(handle)
				{
					clearTimeout(handle);
					handle = null;
					this.setSetting('data', textarea.value);
				}
			}
		});

		this.on('settingsUpdate', () =>
		{
			segmentationDiv.innerHTML = '';

			textarea.value = this.getSetting('data') || '';
			this.setSetting('data', textarea.value);
		});

		const rightDiv = makeDiv({
			parent: section.contentDiv,
			class: 'right',
		});

		const optionsDiv = makeDiv({
			parent: rightDiv,
			class: 'options',
		});

		const options = [
			{id: 'level', label: 'Level', type: 'number', min: '1', max: '3', default: '2'},
			{id: 'minVersion', label: 'Minimum Version', type: 'number', min: '1', max: '40', default: '5'},
			{id: 'versionPadding', label: 'Version Padding', type: 'number', min: '0', max: '39', default: '0'},
		];

		this.makeOptions(optionsDiv, options);

		const resultDiv = makeDiv({
			parent: rightDiv,
			class: 'result',
		});

		const infosDiv = makeDiv({
			parent: resultDiv,
			class: 'infos',
		});

		const infos = [
			{id: 'dataMinVersion', label: 'Minimum Version'},
			{id: 'version', label: 'Version'},
		];

		for(const info of infos)
		{
			const infoDiv = makeDiv('div', {
				parent: infosDiv,
				class: 'info',
			});

			const labelDiv = makeDiv('div', {
				parent: infoDiv,
				class: 'label',
				innerText: info.label
			});

			const valueDiv = makeDiv('div', {
				parent: infoDiv,
				class: 'value',
			});

			info.valueDiv = valueDiv;

			this.on(info.id, (value => valueDiv.innerText = value));
		}

		const segmentationDiv = makeDiv({
			parent: resultDiv,
			class: 'segmentation',
		});

		this.on('segments', (segments => 
		{
			segmentationDiv.innerHTML = '';

			const colors = {
				BYTE: '#2a9d8f',
				ALPHANUMERIC: '#e9c46a',
				NUMERIC: '#f4a261',
				KANJI: '#e76f51',
			};

			segments = JSON.parse(segments);
			for(const segment of segments)
			{
				const segmentDiv = makeDiv('span', {
					parent: segmentationDiv,
					class: 'segment',
					style:
					{
						'background-color': colors[segment.mode]
					},
					title: `Mode: ${segment.mode} Length: ${segment.num}`
				});

				const detailDiv = makeDiv('div', {
					parent: segmentDiv,
					class: 'detail',
				});

				const modeDiv = makeDiv('div', {
					parent: detailDiv,
					class: 'mode',
					innerText: segment.mode[0],
				});

				const lengthDiv = makeDiv('div', {
					parent: detailDiv,
					class: 'length',
					innerText: segment.num,
				});

				const separatorDiv = makeDiv('span', {
					parent: segmentDiv,
					class: 'separator',
					innerText: '|',
				});

				const textDiv = makeDiv('span', {
					parent: segmentDiv,
					class: 'segment-text',
					innerText: segment.text,
				});
			}
		}));

		this.on('dataDirty', () => 
		{
			segmentationDiv.innerHTML = '';

			for(const info of infos)
			{
				info.valueDiv.innerText = "";
			}
		});
	}

	setupStyles(section)
	{
		this.setupImageList('styles', section.contentDiv);
	}

	setupContents(section)
	{
		const imgList = this.setupImageList('contents', section.contentDiv);

		const {optionsDiv} = imgList;

		const options = [
			{id: 'moduleSize', label: 'Module Size', type: 'number', min: '4', max: '16', default: '8', step: '4'},
			{id: 'brightness', label: 'Brightness', type: 'number', min: '0.5', max: '2', default: '1.3', step: '0.05'},
			{id: 'contrast', label: 'Contrast', type: 'number', min: '0.5', max: '2', default: '1.15', step: '0.05'},
		];

		this.makeOptions(optionsDiv, options);
	}

	setupBasic(section)
	{	
		const rootDiv = section.contentDiv;

		const ids = ['edgesImg', 'saliencyImg', 'weightsImg', 'modulesImg', 'codeImg', 'combined'];
		for(const id of ids)
		{
			const wrapper = makeDiv({
				parent: rootDiv,
				class: 'wrapper',
			});

			const img = makeDiv('img', {
				parent: wrapper,
			});

			downloadableImage(img, id);

			this.on(id, (imgSrc) => 
			{
				img.src = imageBase64ToUrl(imgSrc, 'image/jpeg');
				img.parentNode.classList.remove('loading');
			});

			this.on('basicDirty', () => 
			{
				img.src = 'img/loading.gif';
				img.parentNode.classList.add('loading');
			});
		}
	}

	setupStyled(section)
	{	
		const imgList = this.setupImageList('styled', section.contentDiv, false, true);

		const {optionsDiv} = imgList;

		const options = [
			{id: 'training', 		label: 'Training', 				type: 'play', default: true},
			{id: 'epochs', 			label: 'Max Epochs', 			type: 'number', min: '200', max: '50000', default: '800', step: '200'},
			{id: 'learningRate', 	label: 'Learning Rate', 		type: 'number', min: '0.005', max: '0.1', default: '0.01', step: '0.005'},
			{id: 'contentWeight', 	label: 'Content Weight (10^x)', type: 'number', min: '1', max: '30', default: '8', step: '1'},
			{id: 'styleWeight', 	label: 'Style Weight (10^x)', 	type: 'number', min: '1', max: '30', default: '15', step: '1'},
			{id: 'codeWeight', 		label: 'Code Weight (10^x)', 	type: 'number', min: '1', max: '30', default: '12', step: '1'},
			{id: 'discriminant', 	label: 'Discriminant', 			type: 'number', min: '1', max: '127', default: '75', step: '1'},
			{id: 'correct', 		label: 'Correct', 				type: 'number', min: '1', max: '127', default: '55', step: '1'},
		];

		this.makeOptions(optionsDiv, options);

		const infosDiv = makeDiv({
			class: 'infos',
		});

		optionsDiv.parentNode.insertBefore(infosDiv, optionsDiv.nextSibling);

		const infos = {
			'queue': {label: 'Queue'},
			'epoch': {label: 'Epoch'},
			'elapsed': {label: 'Elapsed Time'},
			'averageTime': {label: 'Average Time Per Epoch'},
			'timeLeft': {label: 'Estimated Remaining Time'},
		};

		for(const id in infos)
		{
			const info = infos[id];
			info.id = id;

			const infoDiv = makeDiv('div', {
				parent: infosDiv,
				class: 'info',
			});

			const labelDiv = makeDiv('label', {
				parent: infoDiv,
				class: 'label',
				innerText: info.label
			});

			info.valueDiv = makeDiv('div', {
				parent: infoDiv,
				class: 'value',
				...info
			});

			info.setValue = (value) => 
			{
				info.valueDiv.innerText = value;
			};

			info.dirty = () => 
			{
				info.setValue('...');
			};

			info.dirty();
		}

		const secondsToTime = (value) => 
		{
			const sec_num = parseInt(value, 10); // don't forget the second param
		    let hours   = Math.floor(sec_num / 3600);
		    let minutes = Math.floor((sec_num - (hours * 3600)) / 60);
		    let seconds = sec_num - (hours * 3600) - (minutes * 60);

		    const pad = t => t < 10 ? '0' + t : t;

		    if(hours)
		    {
		    	return pad(hours) + 'h' + pad(minutes) + 'm' + pad(seconds) + 's';
		    }
		    else if(minutes)
		    {
		    	return pad(minutes) + 'm' + pad(seconds) + 's';
		    }
		    else
		    {
		    	return pad(seconds) + 's';
		    }
		};

		this.on('styledUpdate', (data) => 
		{
			const values = {
				epoch: data.epoch,
				elapsed: secondsToTime(data.totalElapsedTime),
				averageTime: Math.round(data.globalAverageEpochTime * 1e4) / 1e4 + 's',
				timeLeft: secondsToTime(data.timeLeft),
			};

			for(const id in values)
			{
				infos[id].setValue(values[id]);
			};

			if(data.gif)
			{
				imgList.previewDiv.src = imageBase64ToUrl(data.gif, 'gif');
			}

			if(data.image)
			{
				imgList.appendImage({data: data.image, path:'image.jpeg'});
			}
		});

		this.on('queue', (data) => 
		{
			let {position, length, status} = data;

			if(!this.getSetting('training'))
			{
				status = 'paused';
			}

			infos['queue'].valueDiv.className = 'value ' + status;

			if(status == 'waiting')
			{
				infos['queue'].setValue(`Queued (#${position + 1} of ${length})`);
			}
			else
			{

				infos['queue'].setValue(capitalizeFirstLetter(status));
			}
		});

		this.on('styledDirty', () => 
		{
			imgList.reset();

			for(const id in infos)
			{
				const info = infos[id];
				info.dirty();
			}
		});
	}

	updateStyles(styles)
	{
		this.updateImageList('styles', styles);
	}

	updateContents(contents)
	{
		this.updateImageList('contents', contents);
	}

	setupImageList(id, rootDiv, selectable = true, downloadable = false)
	{
		const imgList = {};

		imgList.imgs = {};

		imgList.rootDiv = rootDiv;
		imgList.rootDiv.innerHTML = '';
		imgList.rootDiv.classList.add('img-list');

		imgList.controlsDiv = makeDiv({
			parent: imgList.rootDiv,
			class: 'controls',
		});

		imgList.optionsDiv = makeDiv({
			parent: imgList.controlsDiv,
			class: 'options',
		});

		imgList.uploadInput = makeDiv('input', {
			parent: imgList.optionsDiv,
			type: 'file',
			hidden: true,
		});

		if(selectable)
		{
			imgList.uploadDiv = makeDiv('i', {
				parent: imgList.optionsDiv,
				class: 'upload fas fa-upload',
				onclick: () => imgList.uploadInput.click()
			});
		}

		onUploadFile(imgList.uploadInput, (data, name) => {
			data = data.replace(/^data:(.*,)?/, '');
			sendMessage('uploadSessionImage', {data, folder: id, name});
	    });

		imgList.previewDiv = makeDiv('img', {
			parent: imgList.controlsDiv,
			class: 'preview',
		});

		downloadableImage(imgList.previewDiv, id + '_preview');

		imgList.scrollDiv = makeDiv({
			parent: imgList.rootDiv,
			class: 'scroll',
		});

		imgList.onSelect = (img) => 
		{
			Array.from(imgList.rootDiv.querySelectorAll('.selected')).forEach((el) => el.classList.remove('selected'));
			
			if(img)
			{
				img.wrapper.classList.add('selected');
				imgList.selected = img.path;
			}
			else
			{
				imgList.selected = '';
			}

			this.setSetting('selected' + capitalizeFirstLetter(id), imgList.selected);
		};

		this.on('settingsUpdate', () =>
		{
			const image = imgList.imgs[this.getSetting('selected' + capitalizeFirstLetter(id))];
			image && imgList.onSelect(image);
		});

		const scroll = imgList.scrollDiv;
		imgList.appendImage = (image) => 
		{
			const extension = image.path.split('.').splice(-1);

			const wrapper = makeDiv({
				parent: scroll,
				class: 'wrapper ' + (selectable ? 'selectable' : ''),
				onclick: selectable ? () => imgList.onSelect(image) : null,
				title: image.path.split('/').splice(-1)
			});

			const img = makeDiv('img', {
				parent: wrapper,
				src: imageBase64ToUrl(image.data, 'image/' + extension),
			});

			if(downloadable)
			{
				downloadableImage(img, id + '_' + Math.floor(Math.random() * 10000));
			}

			image.wrapper = wrapper;
			image.imgSrc = image.data;
			imgList.imgs[image.path] = image;

			if(image.path == this.getSetting('selected' + capitalizeFirstLetter(id)))
			{
				imgList.onSelect(image);
			}

			if(image.fromSession)
			{
				const deleteDiv = makeDiv({
					parent: wrapper,
					class: 'delete'
				});

				deleteDiv.onclick = () =>
				{
					if(imgList.selected == image.path)
					{
						imgList.onSelect();	
					}

					wrapper.remove();
					delete imgList.imgs[image.path];
					sendMessage('deleteSessionImage', {path: image.path});
				};
			}
		};

		imgList.reset = () =>
		{
			imgList.imgs = [];
			scroll.innerHTML = '';
		}

		this.on(id + 'Preview', (imgSrc) => 
		{
			imgList.previewDiv.src = imageBase64ToUrl(imgSrc, 'image');
			imgList.previewDiv.parentNode.classList.add('loading');
		});

		this.on(id.slice(0, -1) + 'Dirty', () => 
		{
			imgList.previewDiv.src = 'img/loading.gif';
			imgList.previewDiv.parentNode.classList.remove('loading');
		});

		return (this[id + 'ImgList'] = imgList);
	}

	updateImageList(id, images)
	{
		const imgList = this[id + 'ImgList'];

		const scroll = imgList.scrollDiv;
		scroll.innerHTML = '';

		images.sort((s1, s2) => s1.fromSession < s2.fromSession)

		for(const image of images)
		{
			imgList.appendImage(image);
		}

		scroll.insertBefore(makeDiv({class: 'separator'}), scroll.children[images.findIndex(i => !i.fromSession)]);
	}

	onConnectionError()
	{
		
	}
}