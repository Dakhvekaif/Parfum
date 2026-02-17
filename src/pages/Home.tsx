import { useState } from 'react';
import Navbar from '../components/layout/Navbar';
import Hero from '../components/layout/Hero';
import Footer from '../components/layout/Footer';
import ProductCard from '../components/ui/ProductCard';
import QuickViewModal from '../components/ui/QuickViewModal';
import { products, Product } from '../data/products';

const Home = () => {
    const [quickViewProduct, setQuickViewProduct] = useState<Product | null>(null);

    return (
        <div className="min-h-screen bg-brand-white flex flex-col">
            <Navbar />
            <Hero />

            {/* Best Sellers Section */}
            <section className="container py-20 px-4">
                <div className="text-center mb-16">
                    <h2 className="text-3xl lg:text-4xl font-serif mb-4">Best Sellers</h2>
                    <p className="text-brand-darkGray/70 max-w-2xl mx-auto">
                        Our most loved fragrances, curated just for you. Discover the scents that define luxury.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {products.map((product) => (
                        <ProductCard
                            key={product.id}
                            product={product}
                            onQuickView={() => setQuickViewProduct(product)}
                        />
                    ))}
                </div>
            </section>

            {/* Banner Section */}
            <section className="py-20 bg-brand-gray">
                <div className="container px-4 text-center">
                    <h2 className="text-3xl font-serif mb-6">Create Your Signature Scent</h2>
                    <button className="bg-brand-black text-brand-gold px-10 py-4 uppercase tracking-widest text-sm font-semibold hover:bg-brand-gold hover:text-brand-black transition-colors duration-300">
                        Start Creating
                    </button>
                </div>
            </section>

            <Footer />

            {/* Quick View Modal */}
            <QuickViewModal
                product={quickViewProduct}
                isOpen={quickViewProduct !== null}
                onClose={() => setQuickViewProduct(null)}
            />
        </div>
    );
};

export default Home;
