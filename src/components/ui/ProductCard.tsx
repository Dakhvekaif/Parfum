import { Link } from 'react-router-dom';

interface ProductProps {
    id: number;
    name: string;
    price: string;
    image: string;
    category: string;
    isNew?: boolean;
}

interface ProductCardProps {
    product: ProductProps;
    onQuickView?: () => void;
}

const ProductCard = ({ product, onQuickView }: ProductCardProps) => {
    return (
        <div className="group flex flex-col p-4 bg-white rounded-2xl transition-all duration-300 hover:shadow-lg border border-brand-gray/50 hover:border-brand-gold/30 relative">

            {/* Full-card link (sits behind everything) */}
            <Link to={`/product/${product.id}`} className="absolute inset-0 z-10" />

            {/* Image Container */}
            <div className="relative w-full aspect-square mb-4 overflow-hidden rounded-lg bg-brand-gray/10">
                {product.isNew && (
                    <span className="absolute top-2 left-2 bg-brand-black text-brand-gold text-[9px] font-bold px-2 py-1 uppercase tracking-widest z-10">
                        New
                    </span>
                )}
                <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-cover transform transition-transform duration-700 group-hover:scale-110"
                />

                {/* Quick View Overlay */}
                <div className="absolute inset-x-0 bottom-0 p-4 opacity-0 invisible group-hover:visible group-hover:opacity-100 transition-all duration-300 z-30 transform translate-y-2 group-hover:translate-y-0">
                    <button
                        onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            onQuickView?.();
                        }}
                        className="w-full bg-brand-black text-white py-3 text-xs uppercase tracking-widest font-bold hover:bg-brand-gold hover:text-brand-black transition-colors shadow-2xl cursor-pointer"
                    >
                        Quick View
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="text-center w-full px-2">
                <p className="text-[10px] text-brand-gold uppercase tracking-[0.2em] mb-2 font-semibold">
                    {product.category}
                </p>

                <h3 className="font-serif text-lg text-brand-black mb-2 leading-tight group-hover:text-brand-gold transition-colors">
                    {product.name}
                </h3>

                <div className="w-8 h-[1px] bg-brand-gray mx-auto my-3" />

                <p className="font-medium text-brand-darkGray text-sm">
                    {product.price}
                </p>
            </div>
        </div>
    );
};

export default ProductCard;
