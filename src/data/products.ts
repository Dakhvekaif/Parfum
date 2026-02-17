export interface Product {
    id: number;
    name: string;
    category: string;
    price: string;
    image: string;
    isNew: boolean;
    description: string;
    notes: {
        top: string;
        heart: string;
        base: string;
    };
    size: string;
}

export const products: Product[] = [
    {
        id: 1,
        name: "Royal Oud Intense",
        category: "Unisex Perfume",
        price: "450 QAR",
        image: "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?q=80&w=800&auto=format&fit=crop",
        isNew: true,
        description: "A majestic blend of rare oud and warm spices, creating an aura of royalty and sophistication. Perfect for those who command attention.",
        notes: {
            top: "Bergamot, Saffron",
            heart: "Rose, Oud Wood",
            base: "Amber, Musk, Patchouli"
        },
        size: "100 ML"
    },
    {
        id: 2,
        name: "Velvet Rose & Musk",
        category: "Women Perfume",
        price: "380 QAR",
        image: "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?q=80&w=800&auto=format&fit=crop",
        isNew: false,
        description: "An intoxicating bouquet of velvet roses enveloped in soft white musk. A fragrance that whispers elegance and romance.",
        notes: {
            top: "Red Berries, Pear",
            heart: "Damask Rose, Peony",
            base: "White Musk, Vanilla"
        },
        size: "100 ML"
    },
    {
        id: 3,
        name: "Midnight Amber",
        category: "Men Perfume",
        price: "420 QAR",
        image: "https://images.unsplash.com/photo-1541643600914-78b084683601?q=80&w=800&auto=format&fit=crop",
        isNew: true,
        description: "Dark, mysterious, and captivating. Midnight Amber captures the essence of the night with deep woody notes and a hint of spice.",
        notes: {
            top: "Black Pepper, Cardamom",
            heart: "Incense, Amberwood",
            base: "Leather, Tonka Bean"
        },
        size: "100 ML"
    },
    {
        id: 4,
        name: "Crystal Noir Edition",
        category: "Luxury Collection",
        price: "550 QAR",
        image: "https://images.unsplash.com/photo-1616951849649-74dd2dd7e662?q=80&w=800&auto=format&fit=crop",
        isNew: false,
        description: "A luminous fragrance that sparkles like a diamond. Fresh, vibrant, and undeniably luxurious, designed for the modern elite.",
        notes: {
            top: "Yuzu, Pomegranate",
            heart: "Lotus, Magnolia",
            base: "Mahogany, Amber, Musk"
        },
        size: "100 ML"
    }
];
