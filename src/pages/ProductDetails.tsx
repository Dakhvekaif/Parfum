import { useParams, Link } from 'react-router-dom';
import { products } from '../data/products';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import { ArrowLeft, Star, Heart, Share2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ProductDetails = () => {
    const { id } = useParams();
    const product = products.find(p => p.id === Number(id));

    if (!product) {
        return (
            <div className="min-h-screen bg-brand-white flex items-center justify-center">
                <p>Product not found</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-brand-white">
            <Navbar />

            <main className="container px-4 py-8 lg:py-12">
                {/* Breadcrumb / Back */}
                <Link to="/" className="inline-flex items-center text-sm text-brand-darkGray/60 hover:text-brand-black mb-8 transition-colors">
                    <ArrowLeft size={16} className="mr-2" />
                    Back to Collection
                </Link>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">
                    {/* Image Gallery Mock */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="space-y-4"
                    >
                        <div className="aspect-square bg-brand-gray/20 rounded-2xl overflow-hidden relative">
                            {product.isNew && (
                                <span className="absolute top-4 left-4 bg-brand-black text-brand-gold text-xs font-bold px-3 py-1 uppercase tracking-widest z-10">
                                    New Arrival
                                </span>
                            )}
                            <img
                                src={product.image}
                                alt={product.name}
                                className="w-full h-full object-cover mix-blend-multiply"
                            />
                        </div>
                        {/* Thumbnails (Mock) */}
                        <div className="grid grid-cols-4 gap-4">
                            {[1, 2, 3, 4].map((_, i) => (
                                <div key={i} className={`aspect-square rounded-lg border-2 cursor-pointer ${i === 0 ? 'border-brand-black' : 'border-transparent'}`}>
                                    <img src={product.image} className="w-full h-full object-cover rounded-md opacity-70" alt={`View ${i + 1}`} />
                                </div>
                            ))}
                        </div>
                    </motion.div>

                    {/* Product Info */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="flex flex-col justify-center"
                    >
                        <span className="text-brand-gold uppercase tracking-[0.2em] font-bold text-sm mb-2">
                            {product.category}
                        </span>

                        <h1 className="font-serif text-4xl lg:text-5xl text-brand-black mb-4">
                            {product.name}
                        </h1>

                        <div className="flex items-center gap-4 mb-6">
                            <span className="text-2xl font-medium text-brand-black">{product.price}</span>
                            <div className="w-[1px] h-6 bg-brand-gray" />
                            <div className="flex items-center text-brand-gold">
                                <Star size={16} fill="currentColor" />
                                <Star size={16} fill="currentColor" />
                                <Star size={16} fill="currentColor" />
                                <Star size={16} fill="currentColor" />
                                <Star size={16} fill="currentColor" />
                                <span className="ml-2 text-brand-darkGray text-sm underline cursor-pointer">(12 Reviews)</span>
                            </div>
                        </div>

                        <p className="text-brand-darkGray/80 leading-relaxed mb-8 text-lg font-light">
                            {product.description}
                        </p>

                        {/* Fragrance Notes */}
                        <div className="grid grid-cols-3 gap-4 mb-10 py-6 border-y border-brand-gray/30">
                            {[
                                { title: "Top Notes", value: product.notes.top },
                                { title: "Heart Notes", value: product.notes.heart },
                                { title: "Base Notes", value: product.notes.base }
                            ].map((note) => (
                                <div key={note.title} className="text-center">
                                    <span className="block text-xs uppercase tracking-widest text-brand-darkGray/50 mb-1">{note.title}</span>
                                    <span className="font-serif font-medium text-brand-black">{note.value}</span>
                                </div>
                            ))}
                        </div>

                        {/* Actions */}
                        <div className="flex gap-4 mb-8">
                            <button className="flex-1 bg-brand-black text-white py-4 uppercase tracking-[0.1em] font-bold transition-all hover:bg-brand-gold hover:text-brand-black shadow-lg">
                                Add to Cart
                            </button>
                            <button className="p-4 border border-brand-gray rounded-none hover:border-brand-black transition-colors">
                                <Heart size={20} />
                            </button>
                            <button className="p-4 border border-brand-gray rounded-none hover:border-brand-black transition-colors">
                                <Share2 size={20} />
                            </button>
                        </div>

                        <div className="flex items-center gap-2 text-brand-green text-sm font-medium">
                            <span className="w-2 h-2 rounded-full bg-green-500" />
                            In Stock - Ready to Ship
                        </div>
                    </motion.div>
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default ProductDetails;
