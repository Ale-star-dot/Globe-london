// ── GLOBE SHARED DATA ──────────────────────────────────────────────
const GLOBE = {

  events: [
    {
      id: 'solastalgia',
      title: 'Private View: Solastalgia',
      artist: 'Cecily Brown',
      venue: 'White Cube Bermondsey',
      address: 'Bermondsey St, London SE1 3UW',
      neighbourhood: 'south-london',
      category: 'opening',
      date: 'Thu 19 Feb 2026',
      time: '18:00 – 21:00',
      price: 'free-rsvp',
      priceDisplay: 'Free RSVP',
      color: '#C8102E',
      tag: 'Gallery Opening',
      tagClass: 'tag-opening',
      highlight: true,
      description: `Cecily Brown's long-awaited return to White Cube Bermondsey opens with <em>Solastalgia</em> — a suite of large-scale gestural paintings that grapple with climate grief, ecological loss and the persistence of beauty.

The title borrows from the philosopher Glenn Albrecht's coinage for the distress caused by environmental change in one's home. Brown's canvases — ranging from intimate to monumental — deploy her signature technique of layered oil paint, fragmented figuration and restless mark-making to conjure landscapes that hover between lush abundance and catastrophic disintegration.

This is an RSVP-required opening night. Drinks will be served. The exhibition continues until 18 April 2026.`,
      bookingType: 'rsvp',
      url: 'https://whitecube.com/exhibitions/cecily-brown-solastalgia-bermondsey-2026',
      rsvpNote: 'Opening night. Please RSVP to secure your place — spaces are limited.',
    },
    {
      id: 'lagos-collection',
      title: 'Colour & Memory: Works from the Lagos Collection',
      artist: 'Group Exhibition',
      venue: 'Barbican Gallery',
      address: 'Silk St, London EC2Y 8DS',
      neighbourhood: 'east-london',
      category: 'exhibition',
      date: 'Until 6 Mar 2026',
      time: 'Mon–Sun 10:00 – 20:00',
      price: 'paid',
      priceDisplay: '£18 / £12',
      tickets: [
        { type: 'standard', label: 'Standard Entry', price: 18 },
        { type: 'concession', label: 'Concession', price: 12, note: 'Students, seniors & unwaged' },
        { type: 'family', label: 'Family (2 adults + 2 children)', price: 44 },
      ],
      color: '#D4A020',
      tag: 'Exhibition',
      tagClass: 'tag-exhibition',
      description: `A stunning survey of contemporary West African artists exploring identity, colour theory and the politics of memory. Drawn from the remarkable Lagos Collection — assembled over three decades by collector Tokunbo Adesanya — the exhibition brings together over 80 works spanning painting, sculpture, textile and photography.

Artists include El Anatsui, Njideka Akunyili Crosby, Lynette Yiadom-Boakye, and emerging voices from Lagos, Accra and London. The exhibition is structured as a journey through colour — each room devoted to a different chromatic register and its cultural resonances.

A fully illustrated catalogue, public programme and schools provision accompany the exhibition.`,
      bookingType: 'paid',
      url: 'https://www.barbican.org.uk/whats-on/art/colour-and-memory-works-from-the-lagos-collection',
    },
    {
      id: 'kusama-infinity',
      title: 'Yayoi Kusama: Infinity Mirrors',
      artist: 'Yayoi Kusama',
      venue: 'Tate Modern',
      address: 'Bankside, London SE1 9TG',
      neighbourhood: 'south-london',
      category: 'exhibition',
      date: 'Opens 1 Mar 2026',
      time: 'Sun–Thu 10:00 – 18:00, Fri–Sat 10:00 – 22:00',
      price: 'paid',
      priceDisplay: '£25 advance',
      tickets: [
        { type: 'standard', label: 'Adult', price: 25 },
        { type: 'concession', label: 'Concession', price: 18, note: 'With valid ID' },
        { type: 'member', label: 'Tate Member', price: 0, note: 'Free with membership card' },
      ],
      color: '#6B3FA0',
      tag: 'Major Exhibition',
      tagClass: 'tag-major',
      description: `The most anticipated exhibition of the year arrives at Tate Modern. Yayoi Kusama's <em>Infinity Mirror Rooms</em> transform Tate Modern's vast Turbine Hall into an immersive universe of light, reflection, and radical repetition.

Six original Infinity Mirror Rooms — created between 1965 and 2025 — are presented alongside large-scale paintings, soft sculptures and drawings spanning Kusama's nine-decade career. The exhibition traces her journey from early childhood obsessions with dots and flowers through her radical New York period, her return to Japan and her current residency in a Tokyo psychiatric hospital by choice.

This is one of the most popular exhibitions in Tate Modern's history. Advance booking is strongly recommended.`,
      bookingType: 'paid',
      url: 'https://www.tate.org.uk/whats-on/tate-modern/yayoi-kusama',
    },
    {
      id: 'lubaina-himid-talk',
      title: 'In Conversation: Lubaina Himid',
      artist: 'Lubaina Himid CBE',
      venue: 'Serpentine Galleries',
      address: 'Kensington Gardens, London W2 3XA',
      neighbourhood: 'west-end',
      category: 'talk',
      date: 'Thu 19 Feb 2026',
      time: '19:00 – 20:30',
      price: 'paid',
      priceDisplay: '£8 / £5',
      tickets: [
        { type: 'standard', label: 'Standard', price: 8 },
        { type: 'concession', label: 'Concession', price: 5, note: 'Students & unwaged' },
      ],
      color: '#2A5BAD',
      tag: 'Artist Talk',
      tagClass: 'tag-talk',
      description: `Turner Prize-winning artist Lubaina Himid CBE joins Serpentine Director Bettina Korek for an intimate conversation about her ambitious new commission for the Serpentine's South Gallery.

Himid will speak about her lifelong engagement with the politics of representation, her use of colour and pattern as acts of resistance, and what it means to centre Black joy in an art world that has historically marginalised it. She will also reflect on her recent work in opera and theatre set design.

The event is followed by a ticketed drinks reception. All proceeds support the Serpentine's learning programme.`,
      bookingType: 'paid',
      url: 'https://www.serpentinegalleries.org/whats-on/in-conversation-lubaina-himid',
    },
    {
      id: 'zine-fair',
      title: 'The Zine Fair London',
      artist: '200+ Publishers',
      venue: 'Rich Mix',
      address: '35-47 Bethnal Green Rd, London E1 6LA',
      neighbourhood: 'east-london',
      category: 'popup',
      date: 'Sat 21 – Sun 22 Feb 2026',
      time: '10:00 – 18:00',
      price: 'free',
      priceDisplay: 'Free',
      color: '#C8102E',
      tag: 'Pop-up',
      tagClass: 'tag-popup',
      description: `200+ independent publishers, risograph printers and self-publishing artists gather at Rich Mix for London's biggest zine fair. Browse hundreds of handmade publications — from poetry pamphlets to radical political posters, fashion lookbooks to artist research journals.

Live screenprinting runs throughout both days. Workshop programme includes: screen printing for beginners, risograph colour separation, hand-binding and distribution strategies for independent publishers. Book workshops separately.

Admission is free. Bring cash — many tables are cash-only.`,
      bookingType: 'free',
      url: 'https://richmix.org.uk/events/the-zine-fair-london',
      url: 'https://richmix.org.uk/events/the-zine-fair-london',
    },
    {
      id: 'entangled-pasts',
      title: 'Entangled Pasts, 1768–Now',
      artist: 'Art, Colonialism & Change',
      venue: 'Royal Academy of Arts',
      address: 'Burlington House, Piccadilly, London W1J 0BD',
      neighbourhood: 'west-end',
      category: 'exhibition',
      date: 'Until 3 Mar 2026',
      time: 'Daily 10:00 – 18:00',
      price: 'paid',
      priceDisplay: '£22 / £17',
      tickets: [
        { type: 'standard', label: 'Adult', price: 22 },
        { type: 'concession', label: 'Concession', price: 17, note: 'Students, seniors' },
        { type: 'under16', label: 'Under 16', price: 0, note: 'Always free' },
      ],
      color: '#1C6B3A',
      tag: 'Exhibition',
      tagClass: 'tag-exhibition',
      description: `A landmark exhibition at the Royal Academy examines the history of the RA itself — founded in 1768 — within the wider context of the British Empire and its legacies. Over 150 works by 80 artists, spanning more than 250 years, are brought into conversation across history, geography and culture.

The exhibition places canonical RA works by Reynolds, Gainsborough and Turner alongside contemporaneous and contemporary responses from artists across the Caribbean, South Asia, West Africa and the Pacific. Artists include: Kara Walker, Sonia Boyce, Hurvin Anderson and Yinka Shonibare.

Content note: this exhibition contains historical imagery that some visitors may find distressing.`,
      bookingType: 'paid',
      url: 'https://www.royalacademy.org.uk/exhibition/entangled-pasts',
    },
    {
      id: 'ceramics-market',
      title: 'Ceramics & Clay Market',
      artist: '40 Ceramic Artists',
      venue: 'Coal Drops Yard',
      address: "King's Cross, London N1C 4AB",
      neighbourhood: 'north-london',
      category: 'popup',
      date: 'Until Sun 22 Feb 2026',
      time: '10:00 – 18:00',
      price: 'paid',
      priceDisplay: '£2 entry',
      tickets: [
        { type: 'entry', label: 'Entry', price: 2 },
      ],
      color: '#1C6B3A',
      tag: 'Market',
      tagClass: 'tag-popup',
      description: `Forty ceramic artists from across the UK gather at Coal Drops Yard's stunning Victorian gasholders for a weekend of handmade vessels, sculptural objects and raku-fired experiments.

Meet-the-maker sessions run throughout the weekend. Live wheel-throwing demonstrations hourly. A special section is dedicated to emerging ceramicists — recent graduates from RCA, Camberwell and Chelsea.

Entry is £2, redeemable against any purchase. Children under 12 free.`,
      bookingType: 'paid',
      url: 'https://coaldropsyard.com/events/ceramics-clay-market',
    },
    {
      id: 'soutine-dekooning',
      title: 'Soutine / de Kooning: Conversations',
      artist: 'Dual Retrospective',
      venue: 'Courtauld Gallery',
      address: 'Somerset House, Strand, London WC2R 0RN',
      neighbourhood: 'southbank',
      category: 'exhibition',
      date: 'Opens 8 Apr 2026',
      time: 'Daily 10:00 – 18:00',
      price: 'paid',
      priceDisplay: '£18 / £14',
      tickets: [
        { type: 'standard', label: 'Adult', price: 18 },
        { type: 'concession', label: 'Concession', price: 14, note: 'With valid ID' },
      ],
      color: '#8A0B1E',
      tag: 'Coming Soon',
      tagClass: 'tag-exhibition',
      description: `One of the most anticipated shows of 2026 brings together Chaim Soutine and Willem de Kooning in what promises to be an electric dialogue across time. These two painters — one Lithuanian-born in Paris, one Dutch-born in New York — never met, but their shared obsession with the human figure, raw painterly gesture and psychological intensity creates a conversation that feels electric and inevitable.

Works from major international collections including MoMA, the Tate and private lenders will be presented in a newly designed sequence of rooms at the Courtauld, drawing out specific visual rhymes and divergences between the two painters.

Advance booking opens 1 March 2026.`,
      bookingType: 'paid',
      url: 'https://courtauld.ac.uk/whats-on/soutine-de-kooning-conversations',
    },
    {
      id: 'photography-now',
      title: 'Photography Now: Lens-Based Futures',
      artist: 'International Survey',
      venue: "The Photographers' Gallery",
      address: '16-18 Ramillies St, London W1F 7LW',
      neighbourhood: 'west-end',
      category: 'exhibition',
      date: 'Opens 26 Mar 2026',
      time: 'Mon–Sat 11:00 – 18:00, Sun 12:00 – 17:00',
      price: 'free',
      priceDisplay: 'Free entry',
      color: '#2A5BAD',
      tag: 'Exhibition',
      tagClass: 'tag-exhibition',
      description: `The Photographers' Gallery's flagship annual survey returns with 25 artists working across lens-based, moving image and AI-assisted practice. The exhibition takes stock of photography's expanding field — from documentary traditions to speculative futures.

Featured artists include: Deana Lawson, Zanele Muholi, Wolfgang Tillmans and a new generation of practitioners working with machine learning, satellite imaging and archival research. A live programme accompanies the exhibition, including late-night openings every second Friday.`,
      bookingType: 'free',
      url: 'https://thephotographersgallery.org.uk/whats-on/photography-now-lens-based-futures',
      url: 'https://thephotographersgallery.org.uk/whats-on/photography-now-lens-based-futures',
    },
    {
      id: 'fold-photography',
      title: 'FOLD Gallery Popup: Photography',
      artist: 'Emerging Lens-Based Artists',
      venue: 'Exmouth Market',
      address: 'Exmouth Market, Clerkenwell, London EC1R 4QE',
      neighbourhood: 'east-london',
      category: 'popup',
      date: 'Fri 20 – Sun 22 Feb 2026',
      time: '12:00 – 19:00',
      price: 'free',
      priceDisplay: 'Free',
      color: '#6B3FA0',
      tag: 'Pop-up',
      tagClass: 'tag-popup',
      description: `FOLD Gallery brings emerging lens-based artists to an intimate popup space on Exmouth Market. Ten artists, recent graduates from the RCA and Goldsmiths, show new work for the first time in a tightly curated, one-week-only exhibition.

Works include large-format chromogenic prints, zine-based editions, video installations and darkroom experiments. An artist talk takes place Saturday 21 February at 15:00 — free to attend.`,
      bookingType: 'free',
      url: 'https://foldgallery.com/exhibitions/photography-popup-exmouth',
      url: 'https://foldgallery.com/exhibitions/photography-popup-exmouth',
    },
    {
      id: 'art-book-fair',
      title: 'Art Book Fair — Whitechapel',
      artist: '80+ Dealers Worldwide',
      venue: 'Whitechapel Gallery',
      address: '77-82 Whitechapel High St, London E1 7QX',
      neighbourhood: 'east-london',
      category: 'popup',
      date: 'Sat 28 Feb 2026',
      time: '10:00 – 18:00',
      price: 'paid',
      priceDisplay: '£5',
      tickets: [
        { type: 'entry', label: 'Day Entry', price: 5 },
        { type: 'early', label: 'Early Bird (9:00–10:00)', price: 15, note: 'First access, special preview' },
      ],
      color: '#D4A020',
      tag: 'Fair',
      tagClass: 'tag-popup',
      description: `80+ dealers from 20 countries gather at the Whitechapel Gallery for London's most important art book fair. Rare and out-of-print artist monographs, exhibition catalogues, artists' books, multiples and ephemera from the 20th and 21st centuries.

Specialist dealers include: Ursus Books (New York), Printed Matter (New York), Primary Information, Book Works (London) and dozens of independent art bookshops from across Europe.

An early-bird ticket gives you exclusive access from 9:00 with first pick of the most sought-after material.`,
      bookingType: 'paid',
      url: 'https://www.whitechapelgallery.org/whats-on/art-book-fair',
    },
    {
      id: 'south-london-gallery-open',
      title: 'South London Gallery New Season Opening',
      artist: 'Group Exhibition',
      venue: 'South London Gallery',
      address: '65 Peckham Rd, London SE5 8UH',
      neighbourhood: 'south-london',
      category: 'opening',
      date: 'Sat 21 Feb 2026',
      time: '18:00 – 21:00',
      price: 'free',
      priceDisplay: 'Free',
      color: '#1C6B3A',
      tag: 'Opening Night',
      tagClass: 'tag-opening',
      description: `South London Gallery opens its new season with a group exhibition bringing together six artists responding to the gallery's Peckham community — its histories, its people and its rapidly changing landscape.

The opening night is free and open to all. Drinks provided. The exhibition runs until 14 April 2026 and is accompanied by a public programme of workshops, school visits and artist-in-residence projects.`,
      bookingType: 'free',
      url: 'https://www.southlondongallery.org/whats-on/new-season-opening-2026',
      url: 'https://www.southlondongallery.org/whats-on/new-season-opening-2026',
    },
  ],

  neighbourhoods: {
    'east-london': {
      name: 'East London',
      tagline: 'Shoreditch · Hackney · Bethnal Green · Whitechapel',
      description: 'The beating heart of London\'s independent art scene. From the artist-run spaces of Hackney Wick to the commercial galleries of Vyner Street, East London remains the most vibrant and contested art territory in the city.',
      color: '#C8102E',
      icon: '🔴',
      highlights: ['Whitechapel Gallery', 'Barbican Centre', 'Saatchi Gallery East', 'Fold Gallery', 'Hales Gallery'],
    },
    'south-london': {
      name: 'South London',
      tagline: 'Peckham · Bermondsey · Brixton · Camberwell',
      description: 'From the hulking Tate Modern to the intimate spaces of Peckham and Brixton, South London balances institutional weight with grassroots energy. The area has transformed dramatically in two decades.',
      color: '#1C6B3A',
      icon: '🟢',
      highlights: ['Tate Modern', 'White Cube Bermondsey', 'South London Gallery', 'Copeland Gallery', 'Peckham Levels'],
    },
    'west-end': {
      name: 'West End',
      tagline: 'Mayfair · Soho · Fitzrovia · Regent Street',
      description: 'London\'s traditional art market heartland. Mayfair\'s Cork Street and Albemarle Street host major international galleries alongside auction houses, while Soho sustains a more adventurous commercial scene.',
      color: '#2A5BAD',
      icon: '🔵',
      highlights: ['Royal Academy of Arts', 'Serpentine Galleries', 'Hauser & Wirth', 'Gagosian', 'Pace London'],
    },
    'southbank': {
      name: 'Southbank',
      tagline: 'Bankside · Waterloo · Lambeth · Borough',
      description: 'A continuous strip of cultural institutions along the Thames. The Southbank is London at its most publicly ambitious — art, music, theatre and film sharing one of the world\'s great urban waterfronts.',
      color: '#D4A020',
      icon: '🟡',
      highlights: ['Tate Modern', 'Hayward Gallery', 'Courtauld Gallery', 'ICA', 'Somerset House'],
    },
    'north-london': {
      name: 'North London',
      tagline: "King's Cross · Islington · Camden · Hampstead",
      description: 'Home to the revitalised King\'s Cross cultural quarter and the charming gallery villages of Islington and Camden. North London rewards the explorer with everything from Gagosian\'s Victoria Miro to tiny project spaces.',
      color: '#6B3FA0',
      icon: '🟣',
      highlights: ['Victoria Miro', 'Camden Arts Centre', 'Zabludowicz Collection', 'Estorick Collection', 'Parasol Unit'],
    },
  },

  tickerItems: [
    { text: '✦ Private View: Solastalgia — White Cube Bermondsey — Tonight 18:00', id: 'solastalgia' },
    { text: '✦ Colour & Memory — Barbican Gallery — Until 6 Mar', id: 'lagos-collection' },
    { text: '✦ Zine Fair London — Rich Mix Shoreditch — This Weekend', id: 'zine-fair' },
    { text: '✦ Lubaina Himid in Conversation — Serpentine — 19:00 Tonight', id: 'lubaina-himid-talk' },
    { text: '✦ Yayoi Kusama: Infinity Mirrors — Tate Modern — Opens 1 Mar', id: 'kusama-infinity' },
    { text: '✦ Ceramics & Clay Market — Coal Drops Yard — Last 3 Days', id: 'ceramics-market' },
    { text: '✦ Entangled Pasts — Royal Academy — Until 3 Mar', id: 'entangled-pasts' },
    { text: '✦ FOLD Gallery Popup — Exmouth Market — Opens Tomorrow', id: 'fold-photography' },
    { text: '✦ Art Book Fair Whitechapel — 80+ Dealers — Sat 28 Feb', id: 'art-book-fair' },
    { text: '✦ South London Gallery Season Opening — Peckham — This Saturday', id: 'south-london-gallery-open' },
    { text: "✦ Photography Now — The Photographers' Gallery — Opens 26 Mar", id: 'photography-now' },
    { text: '✦ Soutine / de Kooning — Courtauld — Opens 8 Apr', id: 'soutine-dekooning' },
  ],
};
