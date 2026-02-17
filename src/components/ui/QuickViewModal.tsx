import { X, ShoppingBag, Heart, Star } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Product } from '../../data/products';

interface QuickViewModalProps {
    product: Product | null;
    isOpen: boolean;
    onClose: () => void;
}

const QuickViewModal = ({ product, isOpen, onClose }: QuickViewModalProps) => {
    if (!product) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
                    >
                        <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto pointer-events-auto">
                            {/* Close Button */}
                            <button
                                onClick={onClose}
                                className="absolute top-4 right-4 z-10 w-10 h-10 bg-brand-black/80 text-white rounded-full flex items-center justify-center hover:bg-brand-gold hover:text-brand-black transition-colors cursor-pointer"
                            >
                                <X size={18} />
                            </button>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
                                {/* Image */}
                                <div className="relative aspect-square bg-brand-gray/10">
                                    {product.isNew && (
                                        <span className="absolute top-4 left-4 bg-brand-black text-brand-gold text-xs font-bold px-3 py-1 uppercase tracking-widest z-10">
                                            New
                                        </span>
                                    )}
                                    <img
                                        src={product.image}
                                        alt={product.name}
                                        className="w-full h-full object-cover"
                                    />
                                </div>

                                {/* Info */}
                                <div className="p-8 flex flex-col justify-center">
                                    <p className="text-brand-gold uppercase tracking-[0.2em] font-bold text-xs mb-2">
                                        {product.category}
                                    </p>

                                    <h2 className="font-serif text-3xl text-brand-black mb-3">
                                        {product.name}
                                    </h2>

                                    {/* Stars */}
                                    <div className="flex items-center gap-1 mb-4">
                                        {[1, 2, 3, 4, 5].map((s) => (
                                            <Star key={s} size={14} className="text-brand-gold fill-brand-gold" />
                                        ))}
                                        <span className="text-xs text-brand-darkGray/50 ml-2">(12 Reviews)</span>
                                    </div>

                                    <p className="text-2xl font-medium text-brand-black mb-4">
                                        {product.price}
                                    </p>

                                    <p className="text-brand-darkGray/70 text-sm leading-relaxed mb-6">
                                        {product.description}
                                    </p>

                                    {/* Fragrance Notes */}
                                    <div className="grid grid-cols-3 gap-3 mb-6 py-4 border-y border-brand-gray/30">
                                        <div className="text-center">
                                            <span className="block text-[10px] uppercase tracking-widest text-brand-darkGray/40 mb-1">Top</span>
                                            <span className="text-xs font-medium">{product.notes.top}</span>
                                        </div>
                                        <div className="text-center">
                                            <span className="block text-[10px] uppercase tracking-widest text-brand-darkGray/40 mb-1">Heart</span>
                                            <span className="text-xs font-medium">{product.notes.heart}</span>
                                        </div>
                                        <div className="text-center">
                                            <span className="block text-[10px] uppercase tracking-widest text-brand-darkGray/40 mb-1">Base</span>
                                            <span className="text-xs font-medium">{product.notes.base}</span>
                                        </div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex gap-3 mb-4">
                                        <button className="flex-1 bg-brand-black text-white py-3 text-xs uppercase tracking-widest font-bold hover:bg-brand-gold hover:text-brand-black transition-colors flex items-center justify-center gap-2 cursor-pointer">
                                            <ShoppingBag size={16} />
                                            Add to Cart
                                        </button>
                                        <button className="p-3 border border-brand-gray hover:border-brand-black transition-colors cursor-pointer">
                                            <Heart size={18} />
                                        </button>
                                    </div>

                                    <Link
                                        to={`/product/${product.id}`}
                                        onClick={onClose}
                                        className="text-center text-xs uppercase tracking-widest text-brand-darkGray/60 hover:text-brand-gold transition-colors underline underline-offset-4"
                                    >
                                        View Full Details
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default QuickViewModal;
