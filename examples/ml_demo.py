"""Example: machine learning for biology."""

from __future__ import annotations

from biokit.machine_learning.classifiers import KNNClassifier
from biokit.machine_learning.clustering import KMeans
from biokit.machine_learning.datasets import make_blobs, make_classification
from biokit.machine_learning.dimensionality import PCA
from biokit.machine_learning.encoders import LabelEncoder, OneHotSequenceEncoder
from biokit.machine_learning.features import kmer_features
from biokit.machine_learning.metrics import accuracy, silhouette_score
from biokit.machine_learning.splitters import train_test_split


def main() -> None:
    # Classification
    X, y = make_classification(n_samples=60, n_classes=3, random_state=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
    clf = KNNClassifier(k=3).fit(X_train, y_train)
    pred = clf.predict(X_test)
    print(f"KNN accuracy: {accuracy(y_test.tolist(), pred.tolist()):.2%}")

    # Clustering
    X_blobs, _ = make_blobs(n_samples=60, centers=3, random_state=0)
    kmeans = KMeans(k=3, random_state=0)
    labels = kmeans.fit_predict(X_blobs)
    print(f"KMeans silhouette: {silhouette_score(X_blobs, labels):.3f}")

    # Dimensionality reduction
    pca = PCA(n_components=2)
    pca.fit_transform(X)
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio}")

    # Encoders
    enc = LabelEncoder().fit(["a", "b", "c"])
    print(f"LabelEncoder.transform(['a','c']) = {enc.transform(['a', 'c']).tolist()}")

    ohe = OneHotSequenceEncoder()
    print(f"One-hot('ATGC') shape: {ohe.transform('ATGC').shape}")

    # K-mer features
    kmers = kmer_features(["ATGCATGC", "GGGGCCCC"], k=2)
    print(f"K-mer feature matrix shape: {kmers.shape}")


if __name__ == "__main__":
    main()
