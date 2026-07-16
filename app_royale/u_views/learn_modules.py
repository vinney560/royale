from django.shortcuts import render
from app_royale.year_gen import year_gen

"""
    This view renders learnable modules in our reach

    to enable a module, update the lessons to 1+ value
"""
def modules_to_learn(request):
    context = {
        'year': year_gen(),
        'modules': [
            {
                'id': 1,
                'name': 'Learn C',
                'url': '/learn/c/',
                'icon': 'devicon-c-plain',
                'lessons': 14,
            },
            {
                'id': 2,
                'name': 'Learn Flowchart',
                'url': '/learn/flowchart/',
                'icon': 'fas fa-project-diagram',
                'lessons': 7,
            },
            {
                'id': 3,
                'name': 'Learn HTML',
                'url': '/learn/html/',
                'icon': 'devicon-html5-plain',
                'lessons': 5,
            },
            {
                'id': 4,
                'name': 'Learn Assembly',
                'url': '/learn/assembly/',
                'icon': 'devicon-aarch64-plain',
                'lessons': 0,  
            },
            {
                'id': 5,
                'name': 'Learn Python',
                'url': '/learn/python/',
                'icon': 'devicon-python-plain',
                'lessons': 0,
            },
            {
                'id': 6,
                'name': 'Learn JavaScript',
                'url': '/learn/javascript/',
                'icon': 'devicon-javascript-plain',
                'lessons': 0,
            },
        ]
    }
    return render(request, 'modules_to_learn.html', context)

""" 
    This view prepares and renders the learning materials for programming lang,
    Args:
        request (HttpRequest): The HTTP request object containing metadata
            about the request.
    
    Returns:
        HttpResponse: Rendered HTML response for the learn-lang.html template
            with context containing year, icon, module name and notes data.

            icon is sourced from devicons.

            inside notes data:
                type: -- can be; image, doc, video, html, link, audio
                content_url: -- url to the material content.
    
    Template:
        learn-lang.html: Template that renders the learning materials.
"""
def learn_c(request):
    context = {
        'year': year_gen(),
        'icon': 'devicon-c-plain',
        'module': 'C',
        'notes': [
            {
                'id': 1,
                'title': 'History of C',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188074/1784110360493_ioaab6.jpg',
                'type': 'image',
            },
            {
                'id': 2,
                'title': 'What is C?',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188073/1784110363879_mxztal.jpg',
                'type': 'image',
            },
            {
                'id': 3,
                'title': 'Basic syntax',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188076/1784110367723_yixkde.jpg',
                'type': 'image',
            },
            {
                'id': 4,
                'title': 'Input & Output',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188078/1784110389828_lhcn6c.jpg',
                'type': 'image',
            },
            {
                'id': 5,
                'title': 'Operators',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188080/1784110394258_ckmydg.jpg',
                'type': 'image',
            },
            {
                'id': 6,
                'title': 'Loops',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188075/1784110404749_zg5d3g.jpg',
                'type': 'image',
            },
            {
                'id': 7,
                'title': 'Pointers',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188078/1784110415240_njsnmi.jpg',
                'type': 'image',
            },
            {
                'id': 8,
                'title': 'Variables',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188069/1784049049966_msi0sw.jpg',
                'type': 'image',
            },
            {
                'id': 9,
                'title': 'Data Types',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188071/1784049053349_gn5ojt.jpg',
                'type': 'image',
            },
            {
                'id': 10,
                'title': 'Functions',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188073/1784049056750_ng8sqz.jpg',
                'type': 'image',
            },
            {
                'id': 11,
                'title': 'Structures',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188069/1784049059944_gtkgpi.jpg',
                'type': 'image',
            },
            {
                'id': 12,
                'title': 'Union',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188076/1784049063695_msbvlm.jpg',
                'type': 'image',
            },
            {
                'id': 13,
                'title': 'Arrays',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188070/1784049067007_r8ozcl.jpg',
                'type': 'image',
            },
            {
                'id': 14,
                'title': 'File Handling',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188071/1784049070640_j3twbb.jpg',
                'type': 'image',
            },
        ]
    }

    return render(request, "learn-lang.html", context)

def learn_html(request):
    context = {
        'year': year_gen(),
        'icon': 'devicon-html5-plain',
        'module': 'HTML',
        'notes': [
            {
                'id': 1,
                'title': 'Page 1 - Introduction to HTML',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188162/1784048934159_o8tk9b.jpg',
                'type': 'image',
            },
            {
                'id': 2,
                'title': 'Page 2 - HTML Elements, Header & Paragraphs',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188161/1784048939247_euxvft.jpg',
                'type': 'image',
            },
            {
                'id': 3,
                'title': 'Page 3 - HTML Tags, List, Table & Forms',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188162/1784048942897_vtjljj.jpg',
                'type': 'image',
            },
            {
                'id': 4,
                'title': 'Page 4 - HTML Div, Span & Entity',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188163/1784048946546_dywrxc.jpg',
                'type': 'image',
            },
            {
                'id': 5,
                'title': 'Page 5 - HTML Semantic Elements',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188165/1784048949906_ehcwfe.jpg',
                'type': 'image',
            },
        ]
    }

    return render(request, "learn-lang.html", context)

def learn_flowchart(request):
    context = {
        'year': year_gen(),
        'icon': 'fas fa-project-diagram',
        'module': 'flowchart',
        'notes': [
            {
                'id': 1,
                'title': 'Introduction',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188962/1784110204091_daglxs.jpg',
                'type': 'image',
            },
            {
                'id': 2,
                'title': 'Symbols',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188958/1784110210985_m7wigb.jpg',
                'type': 'image',
            },
            {
                'id': 3,
                'title': 'Types',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188962/1784110215386_w12rdu.jpg',
                'type': 'image',
            },
            {
                'id': 4,
                'title': 'Shapes & Uses',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188964/1784110218843_um4tdy.jpg',
                'type': 'image',
            },
            {
                'id': 5,
                'title': 'Merits & Demerits',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188961/1784110222362_hpa0kd.jpg',
                'type': 'image',
            },
            {
                'id': 6,
                'title': 'Rules & Guidelines',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188966/1784110225708_f64amj.jpg',
                'type': 'image',
            },
            {
                'id': 7,
                'title': 'Basic Examples',
                'content_url': 'https://res.cloudinary.com/drma0p4cg/image/upload/v1784188962/1784110229036_gacfv0.jpg',
                'type': 'image',
            },
        ],
    }
    return render(request, "learn-lang.html", context)